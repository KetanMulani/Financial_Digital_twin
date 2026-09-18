import * as React from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { FutureChart } from "@/components/FutureChart";
import { useAppState, useCurrentScenario } from "@/state/AppState";
import { ChevronDown } from "lucide-react";

export function Results() {
  const { go } = useAppState();
  const s = useCurrentScenario();
  const [whyOpen, setWhyOpen] = React.useState(false);
  const [assumptionsOpen, setAssumptionsOpen] = React.useState(false);

  React.useEffect(() => {
    setWhyOpen(false);
    setAssumptionsOpen(false);
  }, [s.key]);

  const tone = (v: string) => (v.startsWith("↓") ? "text-neg" : v.startsWith("↑") ? "text-pos" : "text-text");

  return (
    <div className="animate-fadeIn">
      <section className="text-center py-5 pb-[26px]">
        <div className="inline-flex items-center gap-2 font-display text-[11px] tracking-[0.16em] text-accent mb-[18px]">
          <span className="w-1.5 h-1.5 rounded-full bg-accent" /> <span>{s.kicker}</span>
        </div>
        <h1 className="font-display font-bold text-[clamp(26px,3.6vw,38px)] mb-2.5 tracking-tight">
          Your possible future
        </h1>
        <p className="text-text-dim text-[15px] mx-auto max-w-[520px]">
          Here&rsquo;s how this decision could change your financial trajectory over the next 5 years.
        </p>
      </section>

      <div className="flex gap-[22px] justify-center mb-[22px]">
        <div className="flex items-center gap-2 text-[12.5px] text-text-dim">
          <span className="w-4 h-[3px] rounded-sm bg-greyline" /> Current path
        </div>
        <div className="flex items-center gap-2 text-[12.5px] text-text-dim">
          <span className="w-4 h-[3px] rounded-sm bg-accent shadow-[0_0_6px_1px_rgba(45,212,200,0.35)]" />
          <span>{s.legend}</span>
        </div>
      </div>

      <Card className="p-[30px_36px_20px] max-[480px]:p-[20px_16px_14px] mb-5">
        <FutureChart chart={s.chart} />
      </Card>

      <div className="grid grid-cols-3 max-[860px]:grid-cols-1 gap-4 mb-2">
        <Card className="p-5 px-[22px]">
          <div className="text-[10.5px] tracking-[0.12em] text-text-faint font-display mb-2.5">MONTHLY CASH FLOW</div>
          <div className={`font-display text-[22px] font-bold flex items-center gap-1.5 ${tone(s.delta.cash)}`}>{s.delta.cash}</div>
        </Card>
        <Card className="p-5 px-[22px]">
          <div className="text-[10.5px] tracking-[0.12em] text-text-faint font-display mb-2.5">DEBT</div>
          <div className={`font-display text-[22px] font-bold flex items-center gap-1.5 ${tone(s.delta.debt)}`}>{s.delta.debt}</div>
        </Card>
        <Card className="p-5 px-[22px]">
          <div className="text-[10.5px] tracking-[0.12em] text-text-faint font-display mb-2.5">PROJECTED NET WORTH (5Y)</div>
          <div className={`font-display text-[22px] font-bold flex items-center gap-1.5 ${tone(s.delta.networth)}`}>{s.delta.networth}</div>
        </Card>
      </div>

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
            {s.chain.map((text, i) => (
              <div key={i} className="flex items-start gap-4 pb-[22px] relative last:pb-0">
                {i < s.chain.length - 1 && (
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
            <span className="text-text font-semibold tabular-nums">7% / year</span>
          </div>
          <div className="flex justify-between text-[13px] py-2 border-b border-line">
            <span>Inflation</span>
            <span className="text-text font-semibold tabular-nums">5% / year</span>
          </div>
          <div className="flex justify-between text-[13px] py-2 border-b border-line">
            <span>Investment return</span>
            <span className="text-text font-semibold tabular-nums">10% / year</span>
          </div>
          <div className="flex justify-between text-[13px] py-2">
            <span>{s.rateLabel}</span>
            <span className="text-text font-semibold tabular-nums">{s.rateValue}</span>
          </div>
        </Card>
      )}
      <p className="text-center text-xs text-text-faint mt-5">
        Estimated scenario based on your inputs and these assumptions — not a prediction.
      </p>

      <div className="flex justify-center gap-3.5 mt-[34px] flex-wrap">
        <Button variant="ghost" onClick={() => go("history")}>
          Save to history
        </Button>
        <Button variant="primary" onClick={() => go("home")}>
          Explore another future →
        </Button>
      </div>
    </div>
  );
}
