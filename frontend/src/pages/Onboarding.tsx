import * as React from "react";
import { BrandMark } from "@/components/BrandMark";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useAppState } from "@/state/AppState";

const TOTAL_STEPS = 5;

export function Onboarding() {
  const { profile, setProfile, completeOnboarding, go } = useAppState();
  const [step, setStep] = React.useState(1);
  const [form, setForm] = React.useState({
    income: String(profile.income),
    expenses: String(profile.expenses),
    savings: String(profile.savings),
    debt: String(profile.debt),
    investments: String(profile.investments),
    emergencyFund: String(profile.emergencyFund),
    goalName: profile.goalName,
    goalAmount: String(profile.goalAmount),
  });

  const num = (s: string) => parseInt(s.replace(/[^\d]/g, ""), 10) || 0;

  const finish = () => {
    setProfile({
      income: num(form.income),
      expenses: num(form.expenses),
      savings: num(form.savings),
      debt: num(form.debt),
      investments: num(form.investments),
      emergencyFund: num(form.emergencyFund),
      goalName: form.goalName || "Buy a home",
      goalAmount: num(form.goalAmount),
    });
    completeOnboarding();
  };

  const next = () => (step < TOTAL_STEPS ? setStep(step + 1) : finish());
  const back = () => step > 1 && setStep(step - 1);

  const field = (
    label: string,
    key: keyof typeof form,
    placeholder: string,
    prefix = "₹"
  ) => (
    <div className="mb-[18px]">
      <label className="text-[12.5px] text-text-dim mb-2 block">{label}</label>
      <Input
        prefix={prefix}
        inputMode="numeric"
        placeholder={placeholder}
        value={form[key]}
        onChange={(e) => setForm({ ...form, [key]: e.target.value })}
      />
    </div>
  );

  return (
    <div className="min-h-screen flex items-center justify-center px-5 py-10">
      <div className="w-full max-w-[560px]">
        <div className="flex items-center justify-between mb-7">
          <span className="font-display text-[11.5px] text-text-faint tracking-[0.08em] whitespace-nowrap">
            STEP {step} / {TOTAL_STEPS}
          </span>
          <div className="flex-1 h-[3px] bg-line rounded-full mx-[18px] overflow-hidden">
            <div
              className="h-full bg-accent shadow-[0_0_8px_1px_rgba(45,212,200,0.35)] transition-all duration-400"
              style={{ width: `${(step / TOTAL_STEPS) * 100}%` }}
            />
          </div>
          <span className="w-5 h-5">
            <BrandMark size={20} />
          </span>
        </div>

        <Card className="p-10 max-[480px]:p-6">
          {step === 1 && (
            <div className="animate-fadeIn">
              <div className="font-display text-[11px] tracking-[0.14em] text-accent mb-2.5">
                GETTING TO KNOW YOU
              </div>
              <h2 className="font-display text-[22px] font-semibold mb-[26px]">
                What's your monthly income?
              </h2>
              {field("Take-home income, after tax", "income", "80,000")}
            </div>
          )}
          {step === 2 && (
            <div className="animate-fadeIn">
              <div className="font-display text-[11px] tracking-[0.14em] text-accent mb-2.5">
                GETTING TO KNOW YOU
              </div>
              <h2 className="font-display text-[22px] font-semibold mb-[26px]">
                What do you spend each month?
              </h2>
              {field("Regular expenses — rent, bills, food, etc.", "expenses", "42,000")}
            </div>
          )}
          {step === 3 && (
            <div className="animate-fadeIn">
              <div className="font-display text-[11px] tracking-[0.14em] text-accent mb-2.5">
                GETTING TO KNOW YOU
              </div>
              <h2 className="font-display text-[22px] font-semibold mb-[26px]">
                Savings and any existing debt?
              </h2>
              <div className="grid grid-cols-2 gap-3.5 max-[480px]:grid-cols-1">
                {field("Monthly savings", "savings", "15,000")}
                {field("Existing debt", "debt", "2,10,000")}
              </div>
            </div>
          )}
          {step === 4 && (
            <div className="animate-fadeIn">
              <div className="font-display text-[11px] tracking-[0.14em] text-accent mb-2.5">
                GETTING TO KNOW YOU
              </div>
              <h2 className="font-display text-[22px] font-semibold mb-[26px]">
                Investments and emergency fund?
              </h2>
              <div className="grid grid-cols-2 gap-3.5 max-[480px]:grid-cols-1">
                {field("Current investments", "investments", "3,50,000")}
                {field("Emergency fund", "emergencyFund", "1,20,000")}
              </div>
            </div>
          )}
          {step === 5 && (
            <div className="animate-fadeIn">
              <div className="font-display text-[11px] tracking-[0.14em] text-accent mb-2.5">
                ALMOST DONE
              </div>
              <h2 className="font-display text-[22px] font-semibold mb-[26px]">
                What are you working towards?
              </h2>
              <div className="mb-[18px]">
                <label className="text-[12.5px] text-text-dim mb-2 block">
                  A goal — a house, education, retirement…
                </label>
                <Input
                  placeholder="e.g. Buy a home"
                  value={form.goalName}
                  onChange={(e) => setForm({ ...form, goalName: e.target.value })}
                />
              </div>
              {field("Target amount", "goalAmount", "10,00,000")}
            </div>
          )}

          <div className="flex items-center justify-between mt-[30px]">
            <Button variant="ghost" onClick={back} style={{ visibility: step === 1 ? "hidden" : "visible" }}>
              ← Back
            </Button>
            <Button variant="primary" onClick={next}>
              {step === TOTAL_STEPS ? "Create my Twin" : "Continue"}
            </Button>
          </div>
        </Card>

        <div className="text-center mt-[22px] text-[13px] text-text-faint">
          Just exploring?{" "}
          <button className="bg-transparent border-none text-accent font-semibold text-[13px] cursor-pointer p-0 hover:underline" onClick={() => go("home")}>
            Skip — use sample data
          </button>
        </div>
      </div>
    </div>
  );
}
