import { BrandMark } from "./BrandMark";
import { useAppState } from "@/state/AppState";
import type { ViewKey } from "@/types";
import { Menu } from "lucide-react";

const links: { key: ViewKey; label: string }[] = [
  { key: "home", label: "Home" },
  { key: "twin", label: "Twin" },
  { key: "scenario", label: "Simulate" },
  { key: "history", label: "Insights" },
];

export function Nav() {
  const { view, go, openScenario } = useAppState();

  return (
    <nav className="flex items-center justify-between py-3.5 px-1 pb-6 flex-wrap gap-3.5">
      <div className="flex items-center gap-2.5 cursor-pointer" onClick={() => go("home")}>
        <BrandMark size={26} />
        <span className="font-display font-bold text-base tracking-wide">TWIN</span>
        <span className="font-display text-[10px] tracking-[0.14em] text-accent bg-accent-soft border border-accent/30 px-[7px] py-[3px] rounded-md ml-1 max-[480px]:hidden">
          SIGNAL
        </span>
      </div>

      <div className="flex gap-1 bg-white/[0.02] border border-line rounded-full p-1 order-3 w-full justify-center min-[861px]:order-none min-[861px]:w-auto">
        {links.map((l) => (
          <a
            key={l.key}
            onClick={() => (l.key === "scenario" ? openScenario("loan") : go(l.key))}
            className={`text-[13.5px] font-medium px-4 py-[7px] rounded-full cursor-pointer transition-colors ${
              view === l.key
                ? "text-text bg-panel-2 border border-line-strong"
                : "text-text-dim hover:text-text border border-transparent"
            }`}
          >
            {l.label}
          </a>
        ))}
      </div>

      <div className="flex items-center gap-4">
        <div className="flex items-center gap-[7px] text-[12.5px] text-text-dim max-[640px]:hidden">
          <span className="w-1.5 h-1.5 rounded-full bg-accent shadow-[0_0_8px_1px_rgba(45,212,200,0.35)]" />
          Twin active
        </div>
        <div className="flex items-center gap-2">
          <div className="w-[30px] h-[30px] rounded-full bg-gradient-to-br from-[#3a4552] to-[#1c232c] border border-line-strong flex items-center justify-center font-display text-xs font-semibold text-text-dim">
            A
          </div>
          <span className="text-[13.5px] font-medium">Alex</span>
        </div>
        <div className="w-[30px] h-[30px] rounded-lg flex items-center justify-center text-text-dim border border-transparent hover:border-line-strong hover:text-text cursor-pointer">
          <Menu size={16} />
        </div>
      </div>
    </nav>
  );
}
