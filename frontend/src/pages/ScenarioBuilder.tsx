import * as React from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Slider } from "@/components/ui/slider";
import { useAppState } from "@/state/AppState";
import { scenarios, formatFieldValue } from "@/data/scenarios";
import type { ScenarioField } from "@/types";
import type { Scenario } from "@/services/types";

function buildScenario(
  key: string,
  fields: ScenarioField[],
  monthlyInvestment: number
): { scenario: Scenario; assumptions?: { annual_investment_return: number } } {
  const value = (fieldKey: string) => fields.find((f) => f.key === fieldKey)?.value ?? 0;

  if (key === "invest") {
    return {
      scenario: {
        type: "investment_change",
        new_monthly_contribution: monthlyInvestment + value("amount"),
        start_month: 1,
      },
      assumptions: { annual_investment_return: value("rate") },
    };
  }

  // "loan" and "car" both borrow a lump sum on a fixed schedule.
  return {
    scenario: {
      type: "loan",
      amount: value("amount"),
      interest_rate: value("rate"),
      duration_months: Math.round(value("years") * 12),
      start_month: 1,
    },
  };
}

export function ScenarioBuilder() {
  const { currentScenarioKey, profile, go, runScenarioSimulation, simulationError } = useAppState();
  const base = scenarios[currentScenarioKey];
  const [fields, setFields] = React.useState<ScenarioField[]>(() => base.fields.map((f) => ({ ...f })));
  const [submitting, setSubmitting] = React.useState(false);

  React.useEffect(() => {
    setFields(scenarios[currentScenarioKey].fields.map((f) => ({ ...f })));
  }, [currentScenarioKey]);

  const updateField = (key: string, value: number) => {
    setFields((prev) => prev.map((f) => (f.key === key ? { ...f, value } : f)));
  };

  const simulate = async () => {
    setSubmitting(true);
    const { scenario, assumptions } = buildScenario(
      currentScenarioKey,
      fields,
      profile.monthly_investment
    );
    await runScenarioSimulation(currentScenarioKey, scenario, assumptions);
    setSubmitting(false);
  };

  return (
    <div className="animate-fadeIn">
      <section className="text-center py-5 pb-[30px]">
        <div className="inline-flex items-center gap-2 font-display text-[11px] tracking-[0.16em] text-accent mb-[18px]">
          <span className="w-1.5 h-1.5 rounded-full bg-accent" /> LET&rsquo;S EXPLORE THAT
        </div>
        <h1 className="font-display font-bold text-[clamp(26px,3.6vw,38px)] mb-2.5 tracking-tight">{base.title}</h1>
        <p className="text-text-dim text-[15px] mx-auto max-w-[520px]">
          Adjust the details, then simulate your possible future.
        </p>
      </section>

      <Card className="max-w-[620px] mx-auto p-10 max-[480px]:p-6">
        <div>
          {fields.map((f) => (
            <div key={f.key} className="mb-[22px]">
              <div className="flex items-center justify-between mb-2.5">
                <span className="text-[13px] text-text-dim">{f.label}</span>
                <span className="font-display text-base font-bold tabular-nums">{formatFieldValue(f)}</span>
              </div>
              <Slider
                min={f.min}
                max={f.max}
                step={f.step}
                value={[f.value]}
                onValueChange={(v) => updateField(f.key, v[0])}
              />
            </div>
          ))}
        </div>
        {simulationError && (
          <p className="text-[13px] text-neg mb-4">{simulationError}</p>
        )}
        <div className="flex gap-3 mt-8">
          <Button variant="ghost" className="flex-1" onClick={() => go("home")}>
            Cancel
          </Button>
          <Button variant="primary" className="flex-1" onClick={simulate} disabled={submitting}>
            {submitting ? "Simulating…" : "Simulate Future →"}
          </Button>
        </div>
      </Card>
    </div>
  );
}
