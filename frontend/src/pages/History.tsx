import { Card } from "@/components/ui/card";
import { useAppState } from "@/state/AppState";
import { TrendingUp, Landmark, Car, ArrowLeftRight, Sparkles } from "lucide-react";

const icons: Record<string, React.ReactNode> = {
  loan: <TrendingUp size={17} />,
  invest: <Landmark size={17} />,
  car: <Car size={17} />,
};

function fmtSigned(n: number): string {
  const abs = Math.abs(n);
  const val =
    abs >= 100000
      ? "₹" + (abs / 100000).toFixed(1).replace(".0", "") + "L"
      : "₹" + Math.round(abs / 1000) + "K";
  if (n > 0) return "↑ " + val + " net worth";
  if (n < 0) return "↓ " + val + " net worth";
  return "— ₹0 net worth";
}

export function History() {
  const { simHistory, openResultsFromHistory, go } = useAppState();

  return (
    <div className="animate-fadeIn">
      <section className="text-center py-5 pb-[30px]">
        <div className="inline-flex items-center gap-2 font-display text-[11px] tracking-[0.16em] text-accent mb-[18px]">
          <span className="w-1.5 h-1.5 rounded-full bg-accent" /> SIMULATION HISTORY
        </div>
        <h1 className="font-display font-bold text-[clamp(26px,3.6vw,38px)] mb-2.5 tracking-tight">
          Futures you&rsquo;ve explored
        </h1>
        <p className="text-text-dim text-[15px] mx-auto max-w-[520px]">
          Revisit any past scenario to see the full comparison again.
        </p>
      </section>

      <div className="flex flex-col gap-3 max-w-[680px] mx-auto">
        {simHistory.length === 0 && (
          <p className="text-center text-text-faint text-[13px] mb-2">
            Nothing saved yet — run a simulation and hit "Save to history".
          </p>
        )}

        {simHistory.map((h) => {
          const diff = h.response.comparison?.net_worth_difference ?? 0;
          return (
            <Card
              key={h.id}
              className="flex items-center justify-between py-5 px-6 cursor-pointer hover:border-accent/30 hover:-translate-y-px transition-all"
              onClick={() => openResultsFromHistory(h.id)}
            >
              <div className="flex items-center gap-4 min-w-0">
                <div className="w-[38px] h-[38px] rounded-[10px] bg-accent-soft text-accent flex items-center justify-center flex-shrink-0">
                  {icons[h.meta.scenarioKey] ?? <Sparkles size={17} />}
                </div>
                <div>
                  <p className="text-[14.5px] font-semibold m-0 mb-1">{h.meta.title}</p>
                  <p className="text-xs text-text-faint m-0">{h.date}</p>
                </div>
              </div>
              <div className={`font-display text-[13px] font-bold flex-shrink-0 pl-4 ${diff >= 0 ? "text-pos" : "text-neg"}`}>
                {fmtSigned(diff)}
              </div>
            </Card>
          );
        })}

        <Card
          className="flex items-center justify-between py-5 px-6 cursor-pointer hover:border-accent/30 hover:-translate-y-px transition-all"
          onClick={() => go("home")}
        >
          <div className="flex items-center gap-4 min-w-0">
            <div className="w-[38px] h-[38px] rounded-[10px] bg-accent-soft text-accent flex items-center justify-center flex-shrink-0">
              <ArrowLeftRight size={17} />
            </div>
            <div>
              <p className="text-[14.5px] font-semibold m-0 mb-1">Stay the course</p>
              <p className="text-xs text-text-faint m-0">Baseline · always up to date</p>
            </div>
          </div>
          <div className="font-display text-[13px] font-bold flex-shrink-0 pl-4 text-pos">Reference path</div>
        </Card>
      </div>
    </div>
  );
}
