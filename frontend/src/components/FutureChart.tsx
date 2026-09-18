import * as React from "react";
import type { ScenarioChart } from "@/types";

interface Point {
  x: number;
  y: number;
}

function catmullRomPath(points: Point[]): string {
  if (points.length < 3) {
    return "M " + points.map((p) => `${p.x} ${p.y}`).join(" L ");
  }
  let d = `M ${points[0].x} ${points[0].y}`;
  for (let i = 0; i < points.length - 1; i++) {
    const p0 = points[i - 1] || points[i];
    const p1 = points[i];
    const p2 = points[i + 1];
    const p3 = points[i + 2] || p2;
    const cp1x = p1.x + (p2.x - p0.x) / 6;
    const cp1y = p1.y + (p2.y - p0.y) / 6;
    const cp2x = p2.x - (p3.x - p1.x) / 6;
    const cp2y = p2.y - (p3.y - p1.y) / 6;
    d += ` C ${cp1x} ${cp1y}, ${cp2x} ${cp2y}, ${p2.x} ${p2.y}`;
  }
  return d;
}

const LABELS = ["Now", "1Y", "2Y", "3Y", "4Y", "5Y"];
const SHOW_IDX = [0, 1, 3, 5];

export function FutureChart({ chart }: { chart: ScenarioChart }) {
  const W = 640, H = 260, padL = 34, padR = 20, padT = 16, padB = 34;
  const innerW = W - padL - padR, innerH = H - padT - padB;
  const [drawn, setDrawn] = React.useState(false);

  const { basePts, scenPts, gridYs } = React.useMemo(() => {
    const all = [...chart.baseline, ...chart.scenario];
    const min = Math.min(...all) * 0.9;
    const max = Math.max(...all) * 1.06;
    const n = chart.baseline.length;
    const toXY = (arr: number[]): Point[] =>
      arr.map((v, i) => ({
        x: padL + (i / (n - 1)) * innerW,
        y: padT + (1 - (v - min) / (max - min)) * innerH,
      }));
    const gridYs = [0, 1, 2, 3].map((g) => padT + (g / 3) * innerH);
    return { basePts: toXY(chart.baseline), scenPts: toXY(chart.scenario), gridYs };
  }, [chart, innerW, innerH]);

  React.useEffect(() => {
    setDrawn(false);
    const raf1 = requestAnimationFrame(() => {
      const raf2 = requestAnimationFrame(() => setDrawn(true));
      return () => cancelAnimationFrame(raf2);
    });
    return () => cancelAnimationFrame(raf1);
  }, [chart]);

  const basePath = catmullRomPath(basePts);
  const scenPath = catmullRomPath(scenPts);
  const n = chart.baseline.length;

  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full h-auto block">
      {gridYs.map((gy, i) => (
        <line key={i} x1={padL} x2={W - padR} y1={gy} y2={gy} stroke="rgba(255,255,255,0.07)" strokeWidth={1} />
      ))}
      {SHOW_IDX.map((i) => (
        <text
          key={i}
          x={basePts[i].x}
          y={H - 10}
          textAnchor={i === 0 ? "start" : i === 5 ? "end" : "middle"}
          className="fill-text-faint"
          style={{ fontSize: 11, fontFamily: "Inter, sans-serif" }}
        >
          {LABELS[i]}
        </text>
      ))}
      <path
        d={basePath}
        fill="none"
        stroke="rgba(255,255,255,0.35)"
        strokeWidth={2.5}
        strokeLinecap="round"
        style={{
          strokeDasharray: 900,
          strokeDashoffset: drawn ? 0 : 900,
          transition: "stroke-dashoffset 1.1s cubic-bezier(.2,.7,.3,1)",
        }}
      />
      <path
        d={scenPath}
        fill="none"
        stroke="#2dd4c8"
        strokeWidth={2.5}
        strokeLinecap="round"
        style={{
          filter: "drop-shadow(0 0 6px rgba(45,212,200,0.5))",
          strokeDasharray: 900,
          strokeDashoffset: drawn ? 0 : 900,
          transition: "stroke-dashoffset 1.1s cubic-bezier(.2,.7,.3,1)",
        }}
      />
      <circle cx={basePts[n - 1].x} cy={basePts[n - 1].y} r={4} fill="rgba(255,255,255,0.6)" />
      <circle cx={scenPts[n - 1].x} cy={scenPts[n - 1].y} r={4} fill="#2dd4c8" />
    </svg>
  );
}
