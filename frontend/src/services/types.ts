// Mirrors backend/app/schemas/*.py

export interface BackendProfile {
  id: number;
  monthly_income: number;
  monthly_expenses: number;
  cash_savings: number;
  investments: number;
  monthly_investment: number;
  existing_debt: number;
  debt_interest_rate: number;
  monthly_debt_payment: number;
  financial_goal: number | null;
  created_at: string;
  updated_at: string;
}

export type ProfileUpdatePayload = Omit<
  BackendProfile,
  "id" | "created_at" | "updated_at"
>;

interface ScenarioBase {
  start_month?: number;
}

export interface LoanScenario extends ScenarioBase {
  type: "loan";
  amount: number;
  interest_rate: number;
  duration_months: number;
}

export interface IncomeChangeScenario extends ScenarioBase {
  type: "income_change";
  amount?: number | null;
  percentage?: number | null;
}

export interface ExpenseChangeScenario extends ScenarioBase {
  type: "expense_change";
  amount?: number | null;
  percentage?: number | null;
}

export interface InvestmentChangeScenario extends ScenarioBase {
  type: "investment_change";
  new_monthly_contribution: number;
}

export interface PurchaseScenario extends ScenarioBase {
  type: "purchase";
  price: number;
  down_payment: number;
  financed_amount: number;
  interest_rate?: number | null;
  duration_months?: number | null;
}

export interface IncomeLossScenario extends ScenarioBase {
  type: "income_loss";
  duration_months: number;
  income_reduction: number;
}

export type Scenario =
  | LoanScenario
  | IncomeChangeScenario
  | ExpenseChangeScenario
  | InvestmentChangeScenario
  | PurchaseScenario
  | IncomeLossScenario;

export interface SimulationAssumptions {
  annual_income_growth_rate: number;
  annual_expense_inflation_rate: number;
  annual_investment_return: number;
  annual_savings_interest_rate: number;
}

export interface SimulationRequest {
  projection_months?: number;
  assumptions?: Partial<SimulationAssumptions>;
  scenario?: Scenario | null;
}

export interface TimelinePoint {
  month: number;
  income: number;
  expenses: number;
  debt_payment: number;
  investment_contribution: number;
  monthly_surplus: number;
  cash_savings: number;
  investment_value: number;
  scenario_asset_value: number;
  remaining_debt: number;
  unfunded_deficit: number;
  net_worth: number;
}

export interface FinalSummary {
  final_cash_savings: number;
  final_investment_value: number;
  final_scenario_asset_value: number;
  final_remaining_debt: number;
  final_unfunded_deficit: number;
  final_net_worth: number;
  total_debt_payments: number;
  total_interest_paid: number;
  goal: number | null;
  goal_reached: boolean | null;
}

export interface ProjectionResult {
  timeline: TimelinePoint[];
  final_summary: FinalSummary;
}

export interface SimulationComparison {
  net_worth_difference: number;
  savings_difference: number;
  investment_difference: number;
  asset_difference: number;
  debt_difference: number;
  unfunded_deficit_difference: number;
}

export interface SimulationResponse {
  baseline: ProjectionResult;
  scenario: ProjectionResult | null;
  comparison: SimulationComparison | null;
  warnings: string[];
  assumptions_used: SimulationAssumptions;
}

export interface ScenarioParseResult {
  scenario: Scenario | Record<string, unknown>;
  missing_fields: string[];
  assumptions: string[];
  requires_clarification: boolean;
}
