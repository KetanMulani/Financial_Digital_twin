# TWIN — Ask what could happen

A React port of the "TWIN" personal finance digital-twin design.

## Stack
- React 18 + Vite + TypeScript
- Tailwind CSS (custom design tokens matching the original dark/teal theme)
- shadcn/ui-style components (Button, Input, Card, Slider) built on Radix primitives

## Getting started
\`\`\`bash
npm install
npm run dev
\`\`\`

Then open the printed local URL (usually http://localhost:5173).

## Structure
- `src/state/AppState.tsx` — app-wide view routing, twin profile data, current scenario
- `src/data/scenarios.ts` — loan / invest / car scenario definitions
- `src/components/` — shared UI: Nav, Footer, Gauge, FutureChart (animated SVG line chart), BrandMark
- `src/components/ui/` — shadcn/ui-style primitives
- `src/pages/` — Onboarding, Home, TwinProfile, ScenarioBuilder, Loading, Results, History

## Notes
- The onboarding wizard writes into a shared `TwinProfile` used across Home/Twin pages.
- The chart uses the same Catmull-Rom smoothing math as the original vanilla-JS version, redrawn as React SVG with animated stroke reveal.
- The health gauge, results chart line-draw, and loading squiggle all animate the same way as the source design.
