import type { ScenarioDef } from "@/types";

export const scenarios: Record<string, ScenarioDef> = {
  loan: {
    key: "loan",
    title: "₹10L Personal Loan",
    kicker: "₹10L PERSONAL LOAN",
    legend: "With the loan",
    rateLabel: "Loan interest rate",
    rateValue: "9.5%",
    fields: [
      { key: "amount", label: "Loan amount", prefix: "₹", min: 200000, max: 2000000, step: 50000, value: 1000000, fmt: "lakh" },
      { key: "rate", label: "Interest rate", suffix: "%", min: 7, max: 14, step: 0.5, value: 9.5, fmt: "pct" },
      { key: "years", label: "Duration", suffix: " years", min: 1, max: 10, step: 1, value: 5, fmt: "int" },
    ],
  },
  invest: {
    key: "invest",
    title: "Extra Monthly Investment",
    kicker: "EXTRA MONTHLY INVESTMENT",
    legend: "With extra investing",
    rateLabel: "Expected return",
    rateValue: "10%",
    fields: [
      { key: "amount", label: "Extra monthly investment", prefix: "₹", min: 5000, max: 50000, step: 1000, value: 15000, fmt: "thousand" },
      { key: "rate", label: "Expected annual return", suffix: "%", min: 4, max: 16, step: 0.5, value: 10, fmt: "pct" },
      { key: "years", label: "Duration", suffix: " years", min: 1, max: 10, step: 1, value: 5, fmt: "int" },
    ],
  },
  car: {
    key: "car",
    title: "₹12L Car Purchase",
    kicker: "₹12L CAR PURCHASE",
    legend: "With the car loan",
    rateLabel: "Loan interest rate",
    rateValue: "10.5%",
    fields: [
      { key: "amount", label: "Car price", prefix: "₹", min: 400000, max: 2500000, step: 50000, value: 1200000, fmt: "lakh" },
      { key: "rate", label: "Interest rate", suffix: "%", min: 7, max: 15, step: 0.5, value: 10.5, fmt: "pct" },
      { key: "years", label: "Loan duration", suffix: " years", min: 1, max: 8, step: 1, value: 5, fmt: "int" },
    ],
  },
};

export function formatFieldValue(f: { value: number; fmt: string; suffix?: string }): string {
  if (f.fmt === "lakh") return "₹" + (f.value / 100000).toFixed(1).replace(".0", "") + "L";
  if (f.fmt === "thousand") return "₹" + Math.round(f.value / 1000) + "K";
  if (f.fmt === "pct") return f.value + "%";
  return f.value + (f.suffix ?? "");
}
