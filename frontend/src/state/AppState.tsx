import * as React from "react";
import type { ViewKey, TwinProfile } from "@/types";
import { scenarios } from "@/data/scenarios";

const defaultProfile: TwinProfile = {
  income: 80000,
  expenses: 42000,
  savings: 15000,
  debt: 210000,
  investments: 350000,
  emergencyFund: 120000,
  goalName: "Buy a home",
  goalAmount: 1000000,
};

interface AppStateShape {
  view: ViewKey;
  go: (v: ViewKey) => void;
  onboarded: boolean;
  completeOnboarding: () => void;
  profile: TwinProfile;
  setProfile: React.Dispatch<React.SetStateAction<TwinProfile>>;
  currentScenarioKey: string;
  openScenario: (key: string) => void;
  runSimulation: () => void;
  openResultsFromHistory: (key: string) => void;
}

const AppContext = React.createContext<AppStateShape | null>(null);

export function AppProvider({ children }: { children: React.ReactNode }) {
  const [view, setView] = React.useState<ViewKey>("onboarding");
  const [onboarded, setOnboarded] = React.useState(false);
  const [profile, setProfile] = React.useState<TwinProfile>(defaultProfile);
  const [currentScenarioKey, setCurrentScenarioKey] = React.useState<string>("loan");

  const go = React.useCallback((v: ViewKey) => {
    setView(v);
    window.scrollTo({ top: 0, behavior: "smooth" });
  }, []);

  const completeOnboarding = React.useCallback(() => {
    setOnboarded(true);
    go("home");
  }, [go]);

  const openScenario = React.useCallback(
    (key: string) => {
      setCurrentScenarioKey(key);
      go("scenario");
    },
    [go]
  );

  const runSimulation = React.useCallback(() => {
    go("loading");
    setTimeout(() => {
      go("results");
    }, 1700);
  }, [go]);

  const openResultsFromHistory = React.useCallback(
    (key: string) => {
      setCurrentScenarioKey(key);
      go("results");
    },
    [go]
  );

  const value: AppStateShape = {
    view,
    go,
    onboarded,
    completeOnboarding,
    profile,
    setProfile,
    currentScenarioKey,
    openScenario,
    runSimulation,
    openResultsFromHistory,
  };

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}

export function useAppState() {
  const ctx = React.useContext(AppContext);
  if (!ctx) throw new Error("useAppState must be used within AppProvider");
  return ctx;
}

export function useCurrentScenario() {
  const { currentScenarioKey } = useAppState();
  return scenarios[currentScenarioKey];
}
