import * as React from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Slider } from "@/components/ui/slider";
import { useAppState } from "@/state/AppState";
import { scenarios, formatFieldValue } from "@/data/scenarios";
import type { ScenarioField } from "@/types";

export function ScenarioBuilder() {
  const { currentScenarioKey, go, runSimulation } = useAppState();
  const base = scenarios[currentScenarioKey];
  const [fields, setFields] = React.useState<ScenarioField[]>(() => base.fields.map((f) => ({ ...f })));

  React.useEffect(() => {
    setFields(scenarios[currentScenarioKey].fields.map((f) => ({ ...f })));
  }, [currentScenarioKey]);

  const updateField = (key: string, value: number) => {
    setFields((prev) => prev.map((f) => (f.key === key ? { ...f, value } : f)));
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
        <div className="flex gap-3 mt-8">
          <Button variant="ghost" className="flex-1" onClick={() => go("home")}>
            Cancel
          </Button>
          <Button variant="primary" className="flex-1" onClick={runSimulation}>
            Simulate Future →
          </Button>
        </div>
      </Card>
    </div>
  );
}
