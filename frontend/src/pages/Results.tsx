import * as React from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { FutureChart } from "@/components/FutureChart";
import { useAppState } from "@/state/AppState";
import { ChevronDown } from "lucide-react";
import type { ProjectionResult } from "@/services/types";

function fmtSigned(n: number): string {
  const abs = Math.abs(n);
  const val =
    abs >= 100000
      ? "₹" + (abs / 100000).toFixed(1).replace(".0", "") + "L"
      : "₹" + Math.round(abs / 1000) + "K";
  if (n > 0) return "↑ " + val;
  if (n < 0) return "↓ " + val;
  return "— ₹0";
}

function sampleNetWorth(result: ProjectionResult, nowValue: number): number[] {
  const timeline = result.timeline;
  const total = timeline.length;
  const points = [nowValue];
  for (let i = 1; i <= 5; i++) {
    const idx = Math.min(total - 1, Math.round((total * i) / 5) - 1);
    points.push(timeline[idx].net_worth / 100000);
  }
  return points;
}

export function Results() {
  const { go, profile, lastSimulation, saveCurrentToHistory } = useAppState();
  const [whyOpen, setWhyOpen] = React.useState(false);
  const [assumptionsOpen, setAssumptionsOpen] = React.useState(false);
  const [saved, setSaved] = React.useState(false);

  React.useEffect(() => {
    setWhyOpen(false);
    setAssumptionsOpen(false);
    setSaved(false);
  }, [lastSimulation]);

  if (!lastSimulation) {
    return (
      <div className="text-center py-20 animate-fadeIn">
        <p className="text-text-dim mb-5">No simulation to show yet.</p>
        <Button variant="primary" onClick={() => go("home")}>
          Back to home
        </Button>
      </div>
    );
  }

  const { response, meta } = lastSimulation;
  const { baseline, scenario, comparison, warnings, assumptions_used } = response;

  const nowNetWorth = profile.investments + profile.cash_savings - profile.existing_debt;
  const chart = {
    baseline: sampleNetWorth(baseline, nowNetWorth / 100000),
    scenario: scenario ? sampleNetWorth(scenario, nowNetWorth / 100000) : sampleNetWorth(baseline, nowNetWorth / 100000),
  };

  const cashDelta = scenario
    ? scenario.timeline[scenario.timeline.length - 1].monthly_surplus -
      baseline.timeline[baseline.timeline.length - 1].monthly_surplus
    : 0;

  const tone = (v: number) => (v < 0 ? "text-neg" : v > 0 ? "text-pos" : "text-text");

  return (
    <div className="animate-fadeIn">
      <section className="text-center py-5 pb-[26px]">
        <div className="inline-flex items-center gap-2 font-display text-[11px] tracking-[0.16em] text-accent mb-[18px]">
          <span className="w-1.5 h-1.5 rounded-full bg-accent" /> <span>{meta.kicker}</span>
        </div>
        <h1 className="font-display font-bold text-[clamp(26px,3.6vw,38px)] mb-2.5 tracking-tight">
          Your possible future
        </h1>
        <p className="text-text-dim text-[15px] mx-auto max-w-[520px]">
          Here&rsquo;s how this decision could change your financial trajectory over the projection period.
        </p>
      </section>

      {warnings.length > 0 && (
        <Card className="max-w-[620px] mx-auto p-4 px-5 mb-5 border-l-[3px] border-l-[#e0a53a]">
          {warnings.map((w, i) => (
            <p key={i} className="text-[13px] text-text-dim m-0">
              ⚠ {w}
            </p>
          ))}
        </Card>
      )}

      <div className="flex gap-[22px] justify-center mb-[22px]">
        <div className="flex items-center gap-2 text-[12.5px] text-text-dim">
          <span className="w-4 h-[3px] rounded-sm bg-greyline" /> Current path
        </div>
        <div className="flex items-center gap-2 text-[12.5px] text-text-dim">
          <span className="w-4 h-[3px] rounded-sm bg-accent shadow-[0_0_6px_1px_rgba(45,212,200,0.35)]" />
          <span>{meta.legend}</span>
        </div>
      </div>

      <Card className="p-[30px_36px_20px] max-[480px]:p-[20px_16px_14px] mb-5">
        <FutureChart chart={chart} />
      </Card>

      <div className="grid grid-cols-3 max-[860px]:grid-cols-1 gap-4 mb-2">
        <Card className="p-5 px-[22px]">
          <div className="text-[10.5px] tracking-[0.12em] text-text-faint font-display mb-2.5">MONTHLY CASH FLOW</div>
          <div className={`font-display text-[22px] font-bold flex items-center gap-1.5 ${tone(cashDelta)}`}>{fmtSigned(cashDelta)}</div>
        </Card>
        <Card className="p-5 px-[22px]">
          <div className="text-[10.5px] tracking-[0.12em] text-text-faint font-display mb-2.5">DEBT</div>
          <div className={`font-display text-[22px] font-bold flex items-center gap-1.5 ${tone(comparison?.debt_difference ?? 0)}`}>
            {fmtSigned(comparison?.debt_difference ?? 0)}
          </div>
        </Card>
        <Card className="p-5 px-[22px]">
          <div className="text-[10.5px] tracking-[0.12em] text-text-faint font-display mb-2.5">PROJECTED NET WORTH</div>
          <div className={`font-display text-[22px] font-bold flex items-center gap-1.5 ${tone(comparison?.net_worth_difference ?? 0)}`}>
            {fmtSigned(comparison?.net_worth_difference ?? 0)}
          </div>
        </Card>
      </div>

      {meta.chain.length > 0 && (
        <>
          <div
            className="flex items-center justify-center gap-2 mt-7 cursor-pointer font-display text-sm font-semibold text-accent"
            onClick={() => setWhyOpen((v) => !v)}
          >
            Why did the future change?
            <ChevronDown size={14} className={`transition-transform ${whyOpen ? "rotate-180" : ""}`} />
          </div>
          {whyOpen && (
            <div className="max-w-[520px] mx-auto mt-[26px] animate-fadeIn">
              <Card className="p-7 px-[30px]">
                {meta.chain.map((text, i) => (
                  <div key={i} className="flex items-start gap-4 pb-[22px] relative last:pb-0">
                    {i < meta.chain.length - 1 && (
                      <div className="absolute left-[15px] top-8 bottom-0 w-px bg-line-strong" />
                    )}
                    <div className="w-8 h-8 rounded-full bg-panel-2 border border-line-strong flex items-center justify-center flex-shrink-0 font-display text-xs font-bold text-accent z-10">
                      {i + 1}
                    </div>
                    <div
                      className="text-sm text-text leading-relaxed pt-1 [&_b]:text-accent"
                      dangerouslySetInnerHTML={{ __html: text }}
                    />
                  </div>
                ))}
              </Card>
            </div>
          )}
        </>
      )}

      <div className="text-center mt-[18px]">
        <button
          className="bg-transparent border-none text-accent font-semibold text-[13px] cursor-pointer p-0 hover:underline"
          onClick={() => setAssumptionsOpen((v) => !v)}
        >
          See assumptions used
        </button>
      </div>
      {assumptionsOpen && (
        <Card className="max-w-[520px] mx-auto mt-4 p-5 px-6 animate-fadeIn">
          <div className="flex justify-between text-[13px] py-2 border-b border-line">
            <span>Income growth</span>
            <span className="text-text font-semibold tabular-nums">{assumptions_used.annual_income_growth_rate}% / year</span>
          </div>
          <div className="flex justify-between text-[13px] py-2 border-b border-line">
            <span>Inflation</span>
            <span className="text-text font-semibold tabular-nums">{assumptions_used.annual_expense_inflation_rate}% / year</span>
          </div>
          <div className="flex justify-between text-[13px] py-2 border-b border-line">
            <span>Investment return</span>
            <span className="text-text font-semibold tabular-nums">{assumptions_used.annual_investment_return}% / year</span>
          </div>
          <div className="flex justify-between text-[13px] py-2">
            <span>Savings interest</span>
            <span className="text-text font-semibold tabular-nums">{assumptions_used.annual_savings_interest_rate}% / year</span>
          </div>
        </Card>
      )}
      <p className="text-center text-xs text-text-faint mt-5">
        Estimated scenario based on your inputs and these assumptions — not a prediction.
      </p>

      <div className="flex justify-center gap-3.5 mt-[34px] flex-wrap">
        <Button
          variant="ghost"
          onClick={() => {
            saveCurrentToHistory();
            setSaved(true);
          }}
          disabled={saved}
        >
          {saved ? "Saved ✓" : "Save to history"}
        </Button>
        <Button variant="primary" onClick={() => go("home")}>
          Explore another future →
        </Button>
      </div>
    </div>
  );
}
