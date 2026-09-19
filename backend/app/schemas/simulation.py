from pydantic import BaseModel, ConfigDict, Field

from app.schemas.scenario import Scenario


class SimulationAssumptions(BaseModel):
    """
    Annual rates are supplied as percentages.

    Example:
        10 means 10%
        5 means 5%
    """

    annual_income_growth_rate: float = Field(
        default=5,
        ge=-100,
        le=1000,
    )

    annual_expense_inflation_rate: float = Field(
        default=5,
        ge=-100,
        le=1000,
    )

    annual_investment_return: float = Field(
        default=10,
        ge=-100,
        le=1000,
    )

    annual_savings_interest_rate: float = Field(
        default=3,
        ge=-100,
        le=1000,
    )

    model_config = ConfigDict(extra="forbid")


class SimulationRequest(BaseModel):
    projection_months: int = Field(
        default=60,
        ge=1,
        le=600,
    )

    assumptions: SimulationAssumptions = Field(
        default_factory=SimulationAssumptions
    )

    scenario: Scenario | None = None

    model_config = ConfigDict(extra="forbid")


class TimelinePoint(BaseModel):
    month: int

    income: float
    expenses: float
    debt_payment: float
    investment_contribution: float
    monthly_surplus: float

    cash_savings: float
    investment_value: float
    scenario_asset_value: float

    remaining_debt: float
    unfunded_deficit: float
    net_worth: float


class FinalSummary(BaseModel):
    final_cash_savings: float
    final_investment_value: float
    final_scenario_asset_value: float

    final_remaining_debt: float
    final_unfunded_deficit: float
    final_net_worth: float

    total_debt_payments: float
    total_interest_paid: float

    goal: float | None
    goal_reached: bool | None


class ProjectionResult(BaseModel):
    timeline: list[TimelinePoint]
    final_summary: FinalSummary


class SimulationComparison(BaseModel):
    net_worth_difference: float
    savings_difference: float
    investment_difference: float
    asset_difference: float
    debt_difference: float
    unfunded_deficit_difference: float


class SimulationResponse(BaseModel):
    baseline: ProjectionResult
    scenario: ProjectionResult | None = None
    comparison: SimulationComparison | None = None

    warnings: list[str]
    assumptions_used: SimulationAssumptions