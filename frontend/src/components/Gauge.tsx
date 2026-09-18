import * as React from "react";

export function Gauge({ value = 72, max = 100 }: { value?: number; max?: number }) {
  const [animate, setAnimate] = React.useState(false);
  const r = 83;
  const circumference = 2 * Math.PI * r;
  // Match source design: track drawn as full circle, value arc reveals ~68% by default (dashoffset 146 of 522)
  const fraction = value / max;
  const targetOffset = circumference * (1 - fraction);

  React.useEffect(() => {
    const t = setTimeout(() => setAnimate(true), 50);
    return () => clearTimeout(t);
  }, []);

  return (
    <div className="flex-shrink-0 w-[200px] h-[200px] relative flex items-center justify-center">
      <svg viewBox="0 0 200 200" className="w-full h-full -rotate-90">
        <circle cx="100" cy="100" r={r} fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth="10" />
        <circle
          cx="100"
          cy="100"
          r={r}
          fill="none"
          stroke="#2dd4c8"
          strokeWidth="10"
          strokeLinecap="round"
          style={{
            filter: "drop-shadow(0 0 8px rgba(45,212,200,0.35))",
            strokeDasharray: circumference,
            strokeDashoffset: animate ? targetOffset : circumference,
            transition: "stroke-dashoffset 1.6s cubic-bezier(.2,.7,.3,1) .3s",
          }}
        />
      </svg>
      <div className="absolute text-center">
        <div className="font-display text-[46px] font-bold leading-none">{value}</div>
        <div className="mt-1.5 text-[10.5px] tracking-[0.14em] text-text-faint font-display">
          HEALTH SCORE
        </div>
        <div className="mt-2.5 inline-flex items-center gap-1.5 text-[11.5px] text-accent">
          <span className="w-[5px] h-[5px] rounded-full bg-accent shadow-[0_0_8px_1px_rgba(45,212,200,0.35)]" />
          Steady &amp; Resilient
        </div>
      </div>
    </div>
  );
}
