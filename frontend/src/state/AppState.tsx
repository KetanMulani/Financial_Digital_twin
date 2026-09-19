import * as React from "react";
import type { ViewKey } from "@/types";
import { scenarios } from "@/data/scenarios";
import { getProfile, updateProfile, runSimulation } from "@/services/api";
import type {
  BackendProfile,
  ProfileUpdatePayload,
  Scenario,
  SimulationAssumptions,
  SimulationResponse,
} from "@/services/types";

export interface SimulationMeta {
  scenarioKey: string;
  title: string;
  kicker: string;
  legend: string;
  rateLabel: string;
  rateValue: string;
  chain: string[];
}

export interface SimHistoryEntry {
  id: string;
  date: string;
  response: SimulationResponse;
  meta: SimulationMeta;
}

const defaultProfile: ProfileUpdatePayload = {
  monthly_income: 80000,
  monthly_expenses: 42000,
  cash_savings: 120000,
  investments: 350000,
  monthly_investment: 15000,
  existing_debt: 210000,
  debt_interest_rate: 0,
  monthly_debt_payment: 0,
  financial_goal: 1000000,
};

interface AppStateShape {
  view: ViewKey;
  go: (v: ViewKey) => void;
  onboarded: boolean;
  checkingProfile: boolean;
  completeOnboarding: (payload: ProfileUpdatePayload) => Promise<void>;
  onboardingError: string | null;
  profile: BackendProfile;
  goalName: string;
  setGoalName: (name: string) => void;
  currentScenarioKey: string;
  openScenario: (key: string) => void;
  runScenarioSimulation: (
    scenarioKey: string,
    scenario: Scenario,
    assumptionsOverride?: Partial<SimulationAssumptions>
  ) => Promise<void>;
  simulationError: string | null;
  lastSimulation: { response: SimulationResponse; meta: SimulationMeta } | null;
  simHistory: SimHistoryEntry[];
  saveCurrentToHistory: () => void;
  openResultsFromHistory: (id: string) => void;
}

const AppContext = React.createContext<AppStateShape | null>(null);

function scenarioMeta(scenarioKey: string): Omit<SimulationMeta, "scenarioKey"> {
  const def = scenarios[scenarioKey];
  if (def) {
    return {
      title: def.title,
      kicker: def.kicker,
      legend: def.legend,
      rateLabel: def.rateLabel,
      rateValue: def.rateValue,
      chain: [],
    };
  }
  return {
    title: "Your what-if scenario",
    kicker: "WHAT-IF SCENARIO",
    legend: "With this change",
    rateLabel: "Scenario",
    rateValue: "—",
    chain: [],
  };
}

function buildChain(scenario: Scenario, response: SimulationResponse): string[] {
  const diff = response.comparison?.net_worth_difference ?? 0;
  const fmt = (n: number) => "₹" + Math.round(Math.abs(n)).toLocaleString("en-IN");
  const resultLine =
    diff >= 0
      ? `Result: a <b>higher projected net worth</b> — about <b>${fmt(diff)} more</b> than staying the course.`
      : `Result: a <b>lower projected net worth</b> — about <b>${fmt(diff)} less</b> than staying the course.`;

  if (scenario.type === "loan") {
    return [
      `A <b>${fmt(scenario.amount)} loan</b> at ${scenario.interest_rate}% adds a new monthly obligation.`,
      `That EMI runs for <b>${scenario.duration_months} months</b>, cutting into your monthly surplus.`,
      `Less surplus means <b>slower compounding</b> in your investments over the projection.`,
      resultLine,
    ];
  }

  if (scenario.type === "investment_change") {
    return [
      `Your monthly investment contribution changes to <b>${fmt(scenario.new_monthly_contribution)}</b>.`,
      `That money compounds at the assumed annual return instead of sitting in cash.`,
      resultLine,
    ];
  }

  if (scenario.type === "purchase") {
    return [
      `A <b>${fmt(scenario.price)} purchase</b> is funded with ${fmt(scenario.down_payment)} down` +
        (scenario.financed_amount > 0 ? ` and ${fmt(scenario.financed_amount)} financed.` : "."),
      `Your investment capacity shrinks while any financing is repaid.`,
      resultLine,
    ];
  }

  if (scenario.type === "income_change" || scenario.type === "expense_change") {
    const kind = scenario.type === "income_change" ? "income" : "expenses";
    const delta =
      scenario.amount != null ? fmt(scenario.amount) : `${scenario.percentage}%`;
    return [
      `Your monthly ${kind} change by <b>${delta}</b> starting month ${scenario.start_month ?? 1}.`,
      `That shifts your monthly surplus for the rest of the projection.`,
      resultLine,
    ];
  }

  if (scenario.type === "income_loss") {
    return [
      `Income drops by <b>${scenario.income_reduction}%</b> for <b>${scenario.duration_months} months</b>.`,
      `Your surplus shrinks or turns negative, drawing down cash savings.`,
      resultLine,
    ];
  }

  return [resultLine];
}

export function AppProvider({ children }: { children: React.ReactNode }) {
  const [view, setView] = React.useState<ViewKey>("onboarding");
  const [onboarded, setOnboarded] = React.useState(false);
  const [checkingProfile, setCheckingProfile] = React.useState(true);
  const [onboardingError, setOnboardingError] = React.useState<string | null>(null);
  const [profile, setProfile] = React.useState<BackendProfile>({
    id: 0,
    ...defaultProfile,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  });
  const [goalName, setGoalName] = React.useState("Buy a home");
  const [currentScenarioKey, setCurrentScenarioKey] = React.useState<string>("loan");
  const [simulationError, setSimulationError] = React.useState<string | null>(null);
  const [lastSimulation, setLastSimulation] = React.useState<AppStateShape["lastSimulation"]>(null);
  const [simHistory, setSimHistory] = React.useState<SimHistoryEntry[]>([]);

  React.useEffect(() => {
    let cancelled = false;

    getProfile()
      .then((loaded) => {
        if (cancelled) return;
        if (loaded) {
          setProfile(loaded);
          setOnboarded(true);
          setView("home");
        }
      })
      .catch(() => {
        // Backend unreachable — fall back to onboarding with sample defaults.
      })
      .finally(() => {
        if (!cancelled) setCheckingProfile(false);
      });

    return () => {
      cancelled = true;
    };
  }, []);

  const go = React.useCallback((v: ViewKey) => {
    setView(v);
    window.scrollTo({ top: 0, behavior: "smooth" });
  }, []);

  const completeOnboarding = React.useCallback(
    async (payload: ProfileUpdatePayload) => {
      setOnboardingError(null);
      try {
        const saved = await updateProfile(payload);
        setProfile(saved);
        setOnboarded(true);
        go("home");
      } catch (error) {
        setOnboardingError(
          error instanceof Error ? error.message : "Could not save your profile."
        );
      }
    },
    [go]
  );

  const openScenario = React.useCallback(
    (key: string) => {
      setSimulationError(null);
      setCurrentScenarioKey(key);
      go("scenario");
    },
    [go]
  );

  const runScenarioSimulation = React.useCallback(
    async (
      scenarioKey: string,
      scenario: Scenario,
      assumptionsOverride?: Partial<SimulationAssumptions>
    ) => {
      setSimulationError(null);
      setCurrentScenarioKey(scenarioKey);
      go("loading");

      try {
        const response = await runSimulation({
          projection_months: 60,
          assumptions: assumptionsOverride,
          scenario,
        });

        const meta: SimulationMeta = {
          scenarioKey,
          ...scenarioMeta(scenarioKey),
          chain: buildChain(scenario, response),
        };

        setLastSimulation({ response, meta });
        go("results");
      } catch (error) {
        setSimulationError(
          error instanceof Error ? error.message : "Simulation failed."
        );
        go("scenario");
      }
    },
    [go]
  );

  const saveCurrentToHistory = React.useCallback(() => {
    if (!lastSimulation) return;
    const entry: SimHistoryEntry = {
      id: `${lastSimulation.meta.scenarioKey}-${Date.now()}`,
      date: new Date().toLocaleString("en-IN", {
        hour: "numeric",
        minute: "2-digit",
        day: "numeric",
        month: "short",
      }),
      response: lastSimulation.response,
      meta: lastSimulation.meta,
    };
    setSimHistory((prev) => [entry, ...prev]);
  }, [lastSimulation]);

  const openResultsFromHistory = React.useCallback(
    (id: string) => {
      const entry = simHistory.find((h) => h.id === id);
      if (!entry) return;
      setLastSimulation({ response: entry.response, meta: entry.meta });
      setCurrentScenarioKey(entry.meta.scenarioKey);
      go("results");
    },
    [simHistory, go]
  );

  const value: AppStateShape = {
    view,
    go,
    onboarded,
    checkingProfile,
    completeOnboarding,
    onboardingError,
    profile,
    goalName,
    setGoalName,
    currentScenarioKey,
    openScenario,
    runScenarioSimulation,
    simulationError,
    lastSimulation,
    simHistory,
    saveCurrentToHistory,
    openResultsFromHistory,
  };

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}

export function useAppState() {
  const ctx = React.useContext(AppContext);
  if (!ctx) throw new Error("useAppState must be used within AppProvider");
  return ctx;
}
