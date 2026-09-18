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
    chart: { baseline: [8.4, 11.2, 14.3, 17.8, 21.9, 26.6], scenario: [8.4, 9.6, 11.0, 12.7, 14.7, 17.0] },
    delta: { cash: "↓ ₹21K", debt: "↑ ₹10L", networth: "↓ ₹9.6L" },
    chain: [
      "A <b>₹10L loan</b> at 9.5% adds a new monthly obligation to your Twin.",
      "That works out to roughly <b>₹21,247 EMI</b> every month.",
      "Your monthly surplus drops, leaving <b>less to invest</b> each month.",
      "Lower monthly investing means <b>slower compounding</b> over 5 years.",
      "Result: a <b>lower projected net worth</b> versus staying the course.",
    ],
  },
  invest: {
    key: "invest",
    title: "₹15K/month Investment",
    kicker: "₹15K/MONTH EXTRA INVESTMENT",
    legend: "With extra investing",
    rateLabel: "Expected return",
    rateValue: "10%",
    fields: [
      { key: "amount", label: "Extra monthly investment", prefix: "₹", min: 5000, max: 50000, step: 1000, value: 15000, fmt: "thousand" },
      { key: "rate", label: "Expected annual return", suffix: "%", min: 4, max: 16, step: 0.5, value: 10, fmt: "pct" },
      { key: "years", label: "Duration", suffix: " years", min: 1, max: 10, step: 1, value: 5, fmt: "int" },
    ],
    chart: { baseline: [8.4, 11.2, 14.3, 17.8, 21.9, 26.6], scenario: [8.4, 12.4, 16.9, 22.2, 28.5, 36.0] },
    delta: { cash: "↓ ₹15K", debt: "— ₹0", networth: "↑ ₹9.4L" },
    chain: [
      "You commit an extra <b>₹15,000/month</b> toward investments.",
      "Your available monthly surplus is <b>reduced by that amount</b>.",
      "But that money compounds at an assumed <b>10% annual return</b>.",
      "Over 5 years, compounding <b>outweighs</b> the smaller monthly surplus.",
      "Result: a <b>meaningfully higher projected net worth</b> than the current path.",
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
    chart: { baseline: [8.4, 11.2, 14.3, 17.8, 21.9, 26.6], scenario: [8.4, 9.9, 11.6, 13.6, 15.9, 18.6] },
    delta: { cash: "↓ ₹18K", debt: "↑ ₹12L", networth: "↓ ₹8.0L" },
    chain: [
      "A <b>₹12L car</b> is financed with a new auto loan at 10.5%.",
      "This adds roughly <b>₹18,300 EMI</b> to your monthly obligations.",
      "Your investment capacity <b>shrinks</b> for the loan's duration.",
      "Less monthly investing means <b>reduced compounding</b> over 5 years.",
      "Result: a <b>lower projected net worth</b>, even though you gain an asset.",
    ],
  },
};

export function formatFieldValue(f: { value: number; fmt: string; suffix?: string }): string {
  if (f.fmt === "lakh") return "₹" + (f.value / 100000).toFixed(1).replace(".0", "") + "L";
  if (f.fmt === "thousand") return "₹" + Math.round(f.value / 1000) + "K";
  if (f.fmt === "pct") return f.value + "%";
  return f.value + (f.suffix ?? "");
}

export const historyEntries = [
  { key: "loan", title: "₹10L personal loan", date: "Simulated today · 08:41 AM", badge: "↓ ₹9.6L net worth", tone: "neg" as const },
  { key: "invest", title: "₹15K/month extra investment", date: "Yesterday · 7:12 PM", badge: "↑ ₹9.4L net worth", tone: "pos" as const },
  { key: "car", title: "Buying a ₹12L car", date: "3 days ago · 6:05 PM", badge: "↓ ₹8.0L net worth", tone: "neg" as const },
];
