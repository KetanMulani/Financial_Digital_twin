export type ViewKey =
  | "onboarding"
  | "home"
  | "twin"
  | "scenario"
  | "loading"
  | "results"
  | "history";

export type FieldFormat = "lakh" | "thousand" | "pct" | "int";

export interface ScenarioField {
  key: string;
  label: string;
  prefix?: string;
  suffix?: string;
  min: number;
  max: number;
  step: number;
  value: number;
  fmt: FieldFormat;
}

export interface ScenarioChart {
  baseline: number[];
  scenario: number[];
}

export interface ScenarioDef {
  key: string;
  title: string;
  kicker: string;
  legend: string;
  rateLabel: string;
  rateValue: string;
  fields: ScenarioField[];
}
