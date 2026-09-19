import * as React from "react";
import { Card } from "@/components/ui/card";
import { Gauge } from "@/components/Gauge";
import { useAppState } from "@/state/AppState";
import { Search, ArrowRight } from "lucide-react";
import { parseScenario } from "@/services/api";
import type { Scenario } from "@/services/types";

function fmtLakh(n: number) {
  return "₹" + (n / 100000).toFixed(1).replace(".0", "") + "L";
}
function fmtK(n: number) {
  return "₹" + Math.round(n / 1000) + "K";
}
function fmtTime(d: Date) {
  let h = d.getHours();
  const m = d.getMinutes();
  const ampm = h >= 12 ? "PM" : "AM";
  let hh = h % 12;
  if (hh === 0) hh = 12;
  const mm = m < 10 ? "0" + m : String(m);
  return `${hh}:${mm} ${ampm}`;
}

export function Home() {
  const { profile, openScenario, runScenarioSimulation, go } = useAppState();
  const [now, setNow] = React.useState(new Date());
  const [ask, setAsk] = React.useState("");
  const [asking, setAsking] = React.useState(false);
  const [askNote, setAskNote] = React.useState<string | null>(null);

  React.useEffect(() => {
    const t = setInterval(() => setNow(new Date()), 30000);
    return () => clearInterval(t);
  }, []);

  const hour = now.getHours();
  const greeting = hour < 12 ? "Good morning" : hour < 18 ? "Good afternoon" : "Good evening";

  const surplus = profile.monthly_income - profile.monthly_expenses;
  const netWorth = profile.investments + profile.cash_savings - profile.existing_debt;

  const send = async () => {
    if (!ask.trim() || asking) return;
    setAsking(true);
    setAskNote(null);

    try {
      const parsed = await parseScenario(ask);

      if (parsed.requires_clarification) {
        setAskNote(
          parsed.clarification_questions.length
            ? parsed.clarification_questions.join(" ")
            : "I need a bit more detail to run that simulation."
        );
        return;
      }

      const scenario = parsed.scenario as Scenario;
      await runScenarioSimulation(scenario.type, scenario);
    } catch (error) {
      setAskNote(error instanceof Error ? error.message : "Couldn't parse that scenario.");
    } finally {
      setAsking(false);
    }
  };

  const askAndGo = (text: string, key: string) => {
    setAsk(text);
    setAskNote(null);
    setTimeout(() => openScenario(key), 250);
  };

  return (
    <div className="animate-fadeIn">
      <section className="text-center py-5 pb-[34px]">
        <div className="inline-flex items-center gap-2 font-display text-[11px] tracking-[0.16em] text-accent mb-[18px]">
          <span className="w-1.5 h-1.5 rounded-full bg-accent shadow-[0_0_10px_2px_rgba(45,212,200,0.35)]" />
          SYNAPSE SYNCHRONIZED · <span>{fmtTime(now)}</span>
        </div>
        <h1 className="font-display font-bold text-[clamp(30px,4.2vw,44px)] mb-3 tracking-tight">
          {greeting}, Alex
        </h1>
        <p className="text-text-dim text-[15.5px] m-0">
          Let's see how your financial world is doing today.
        </p>
      </section>

      <Card className="p-[42px_44px] max-[860px]:p-[34px_24px] flex items-center gap-14 flex-wrap max-[860px]:flex-col">
        <Gauge value={72} />
        <div className="flex-1 flex flex-col w-full">
          <div className="flex items-center justify-between py-4 border-b border-line pt-0.5">
            <div>
              <div className="text-[10.5px] tracking-[0.14em] text-text-faint font-display mb-2">NET WORTH</div>
              <div className="font-display text-[26px] font-bold tabular-nums">{fmtLakh(netWorth)}</div>
            </div>
          </div>
          <div className="flex items-center justify-between py-4 border-b border-line">
            <div>
              <div className="text-[10.5px] tracking-[0.14em] text-text-faint font-display mb-2">MONTHLY SURPLUS</div>
              <div className="font-display text-[26px] font-bold tabular-nums">{fmtK(surplus)}</div>
            </div>
            <div className="text-[12.5px] text-text-dim mt-1.5">✓ Post obligations</div>
          </div>
          <div className="flex items-center justify-between py-4 pb-0.5">
            <div>
              <div className="text-[10.5px] tracking-[0.14em] text-text-faint font-display mb-2">EXISTING DEBT</div>
              <div className="font-display text-[26px] font-bold tabular-nums">{fmtLakh(profile.existing_debt)}</div>
            </div>
          </div>
        </div>
      </Card>

      <section className="text-center py-[54px] pb-9">
        <h2 className="font-display text-[21px] font-semibold mb-[22px]">What are you thinking about?</h2>
        <div className="max-w-[620px] mx-auto flex items-center gap-3 bg-panel border border-line-strong rounded-full py-2 pl-[22px] pr-2 focus-within:border-accent/50 focus-within:shadow-[0_0_0_4px_rgba(45,212,200,0.14)] transition-all">
          <Search size={18} className="text-text-faint flex-shrink-0" />
          <input
            className="flex-1 bg-transparent border-none outline-none text-text text-[15px] py-2.5 placeholder:text-text-faint"
            placeholder="Ask what could happen…"
            value={ask}
            onChange={(e) => setAsk(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && send()}
            disabled={asking}
          />
          <button
            aria-label="Send"
            onClick={send}
            disabled={asking}
            className="w-[42px] h-[42px] rounded-full flex-shrink-0 bg-accent border-none cursor-pointer flex items-center justify-center shadow-[0_0_18px_1px_rgba(45,212,200,0.35)] hover:scale-[1.06] transition-transform disabled:opacity-50"
          >
            <ArrowRight size={16} className="text-[#06110f]" />
          </button>
        </div>
        {askNote && (
          <p className="text-[13px] text-text-dim mt-3 max-w-[520px] mx-auto">{askNote}</p>
        )}
        <div className="flex flex-wrap justify-center gap-2.5 mt-5 max-[480px]:flex-col max-[480px]:items-stretch">
          <button
            className="inline-flex items-center justify-center gap-1.5 text-[13px] text-text-dim border border-line bg-white/[0.015] px-4 py-2 rounded-full cursor-pointer hover:text-text hover:border-accent/35 hover:bg-accent-soft transition-colors"
            onClick={() => askAndGo("What if I take a ₹10L loan?", "loan")}
          >
            <span className="w-[5px] h-[5px] rounded-full bg-accent" /> What if I take a ₹10L loan?
          </button>
          <button
            className="inline-flex items-center justify-center gap-1.5 text-[13px] text-text-dim border border-line bg-white/[0.015] px-4 py-2 rounded-full cursor-pointer hover:text-text hover:border-accent/35 hover:bg-accent-soft transition-colors"
            onClick={() => askAndGo("What if I invest ₹15K more?", "invest")}
          >
            <span className="w-[5px] h-[5px] rounded-full bg-accent" /> What if I invest ₹15K more?
          </button>
          <button
            className="inline-flex items-center justify-center gap-1.5 text-[13px] text-text-dim border border-line bg-white/[0.015] px-4 py-2 rounded-full cursor-pointer hover:text-text hover:border-accent/35 hover:bg-accent-soft transition-colors"
            onClick={() => askAndGo("Can I afford a ₹12L car?", "car")}
          >
            <span className="w-[5px] h-[5px] rounded-full bg-accent" /> Can I afford a car?
          </button>
        </div>
      </section>

      <Card className="max-w-[620px] mx-auto p-5 px-6 border-l-[3px] border-l-accent rounded-md flex items-center justify-between gap-5 flex-wrap max-[480px]:flex-col max-[480px]:items-stretch max-[480px]:text-left">
        <div>
          <div className="flex items-center gap-1.5 text-[11.5px] text-accent font-semibold mb-2">
            ✨ YOUR TWIN NOTICED
          </div>
          <p className="text-[14.5px] font-semibold m-0 mb-1">Your monthly surplus is {fmtK(surplus)}.</p>
          <p className="text-[12.5px] text-text-dim m-0">
            Emergency buffer covers{" "}
            <b className="text-text">
              {profile.monthly_expenses ? (profile.cash_savings / profile.monthly_expenses).toFixed(1) : "0"}
            </b>{" "}
            months of expenses.
          </p>
        </div>
        <button
          onClick={() => go("history")}
          className="flex-shrink-0 font-display text-[11.5px] font-semibold tracking-wide text-accent bg-transparent border border-accent/30 px-4 py-2.5 rounded-lg cursor-pointer whitespace-nowrap hover:bg-accent-soft hover:border-accent/55 transition-colors max-[480px]:self-start"
        >
          EXPLORE →
        </button>
      </Card>
    </div>
  );
}
