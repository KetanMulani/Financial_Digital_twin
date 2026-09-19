import { Card } from "@/components/ui/card";
import { useAppState } from "@/state/AppState";
import { Landmark, List, PiggyBank, ArrowLeftRight, TrendingUp, Shield } from "lucide-react";

function fmtLakh(n: number) {
  return "₹" + (n / 100000).toFixed(1).replace(".0", "") + "L";
}
function fmtFull(n: number) {
  return "₹" + n.toLocaleString("en-IN");
}

export function TwinProfile() {
  const { profile } = useAppState();
  const investmentRate = profile.monthly_income
    ? ((profile.monthly_investment / profile.monthly_income) * 100).toFixed(2)
    : "0";
  const emergencyMonths = profile.monthly_expenses
    ? (profile.cash_savings / profile.monthly_expenses).toFixed(1)
    : "0";

  const items = [
    { icon: <Landmark size={16} />, label: "MONTHLY INCOME", value: fmtFull(profile.monthly_income), note: "Take-home, after tax" },
    { icon: <List size={16} />, label: "MONTHLY EXPENSES", value: fmtFull(profile.monthly_expenses), note: "Rent, bills, food & more" },
    { icon: <PiggyBank size={16} />, label: "MONTHLY INVESTMENT", value: fmtFull(profile.monthly_investment), note: `${investmentRate}% of income` },
    { icon: <ArrowLeftRight size={16} />, label: "EXISTING DEBT", value: fmtLakh(profile.existing_debt), note: profile.monthly_debt_payment ? `${fmtFull(profile.monthly_debt_payment)}/mo EMI` : "No active EMI" },
    { icon: <TrendingUp size={16} />, label: "INVESTMENTS", value: fmtLakh(profile.investments), note: "Across mutual funds & equity" },
    { icon: <Shield size={16} />, label: "EMERGENCY FUND", value: fmtLakh(profile.cash_savings), note: `Covers ${emergencyMonths} months` },
  ];

  return (
    <div className="animate-fadeIn">
      <section className="text-center py-5 pb-[34px]">
        <div className="inline-flex items-center gap-2 font-display text-[11px] tracking-[0.16em] text-accent mb-[18px]">
          <span className="w-1.5 h-1.5 rounded-full bg-accent" /> YOUR DIGITAL TWIN
        </div>
        <h1 className="font-display font-bold text-[clamp(26px,3.6vw,38px)] mb-2.5 tracking-tight">
          Alex&rsquo;s financial state
        </h1>
        <p className="text-text-dim text-[15px] mx-auto max-w-[520px]">
          A live structured model of your money — not just numbers, but how they move together.
        </p>
      </section>

      <div className="grid grid-cols-3 max-[860px]:grid-cols-2 max-[480px]:grid-cols-1 gap-4 mb-[34px]">
        {items.map((it) => (
          <Card key={it.label} className="p-[22px_24px]">
            <div className="w-[34px] h-[34px] rounded-[9px] bg-accent-soft text-accent flex items-center justify-center mb-4">
              {it.icon}
            </div>
            <div className="text-[10.5px] tracking-[0.12em] text-text-faint font-display mb-2">{it.label}</div>
            <div className="font-display text-[22px] font-bold">{it.value}</div>
            <div className="text-xs text-text-dim mt-1.5">{it.note}</div>
          </Card>
        ))}
      </div>

      <Card className="p-[34px_40px] max-[480px]:p-6">
        <h3 className="font-display text-base font-semibold mb-[26px]">How your money moves</h3>
        <div className="flex items-center justify-center gap-2.5 flex-wrap">
          <span className="font-display text-[13px] font-semibold px-[18px] py-[11px] rounded-[10px] bg-white/[0.02] border border-line-strong whitespace-nowrap">
            Income
          </span>
          <span className="text-text-faint text-base">→</span>
          <span className="font-display text-[13px] font-semibold px-[18px] py-[11px] rounded-[10px] text-accent border border-accent/35 bg-accent-soft whitespace-nowrap">
            Monthly surplus
          </span>
          <span className="text-text-faint text-base">→</span>
          <span className="font-display text-[13px] font-semibold px-[18px] py-[11px] rounded-[10px] bg-white/[0.02] border border-line-strong whitespace-nowrap">
            Savings
          </span>
          <span className="text-text-faint text-base">→</span>
          <span className="font-display text-[13px] font-semibold px-[18px] py-[11px] rounded-[10px] bg-white/[0.02] border border-line-strong whitespace-nowrap">
            Investments
          </span>
          <span className="text-text-faint text-base">→</span>
          <span className="font-display text-[13px] font-semibold px-[18px] py-[11px] rounded-[10px] text-accent border border-accent/35 bg-accent-soft whitespace-nowrap">
            Future wealth
          </span>
        </div>
      </Card>
    </div>
  );
}
