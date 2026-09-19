from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.scenario import Scenario


class SimulationAssumptions(BaseModel):
    """Annual rates expressed as percentages."""

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


class MonteCarloConfig(BaseModel):
    enabled: bool = False
    simulations: int = Field(
        default=1000,
        ge=100,
        le=10_000,
    )
    seed: int = Field(
        default=42,
        ge=0,
        le=2_147_483_647,
    )
    investment_return_std: float = Field(
        default=5,
        ge=0,
        le=100,
        description="Standard deviation in percentage points",
    )
    income_growth_std: float = Field(
        default=2,
        ge=0,
        le=100,
        description="Standard deviation in percentage points",
    )
    expense_inflation_std: float = Field(
        default=2,
        ge=0,
        le=100,
        description="Standard deviation in percentage points",
    )

    model_config = ConfigDict(extra="forbid")


SensitivityParameter = Literal[
    "monthly_income",
    "monthly_expenses",
    "cash_savings",
    "investments",
    "monthly_investment",
    "existing_debt",
    "debt_interest_rate",
    "monthly_debt_payment",
    "annual_income_growth_rate",
    "annual_expense_inflation_rate",
    "annual_investment_return",
    "annual_savings_interest_rate",
]


DEFAULT_SENSITIVITY_PARAMETERS: list[
    SensitivityParameter
] = [
    "monthly_income",
    "monthly_expenses",
    "monthly_investment",
    "annual_income_growth_rate",
    "annual_expense_inflation_rate",
    "annual_investment_return",
]


class SensitivityConfig(BaseModel):
    enabled: bool = False

    parameters: list[SensitivityParameter] = Field(
        default_factory=lambda: (
            DEFAULT_SENSITIVITY_PARAMETERS.copy()
        ),
        min_length=1,
    )

    variation_percent: float = Field(
        default=10,
        gt=0,
        le=100,
        description=(
            "Percentage by which each selected input is "
            "decreased and increased during one-at-a-time "
            "sensitivity analysis"
        ),
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

    monte_carlo: MonteCarloConfig = Field(
        default_factory=MonteCarloConfig
    )

    sensitivity: SensitivityConfig = Field(
        default_factory=SensitivityConfig
    )

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


class PercentileSummary(BaseModel):
    p10: float
    p50: float
    p90: float
    mean: float
    minimum: float
    maximum: float


class MonteCarloResult(BaseModel):
    simulations: int
    seed: int

    final_net_worth: PercentileSummary
    final_cash_savings: PercentileSummary
    final_investment_value: PercentileSummary

    probability_of_reaching_goal: float | None
    probability_of_cash_depletion: float
    probability_of_unfunded_deficit: float

    sampling_configuration: dict[
        str,
        dict[str, float],
    ]


class MonteCarloComparison(BaseModel):
    net_worth_p10_difference: float
    net_worth_p50_difference: float
    net_worth_p90_difference: float

    goal_probability_difference: float | None
    cash_depletion_probability_difference: float
    unfunded_deficit_probability_difference: float


class MonteCarloBundle(BaseModel):
    baseline: MonteCarloResult
    scenario: MonteCarloResult | None = None
    comparison: MonteCarloComparison | None = None


class SensitivityParameterResult(BaseModel):
    parameter: SensitivityParameter

    base_value: float
    low_value: float
    high_value: float

    base_final_net_worth: float
    low_final_net_worth: float
    high_final_net_worth: float

    low_change: float
    high_change: float
    net_worth_range: float
    normalized_impact: float


class SensitivityResult(BaseModel):
    variation_percent: float
    base_final_net_worth: float

    ranking: list[SensitivityParameterResult]

    most_sensitive_parameter: (
        SensitivityParameter | None
    )


class SimulationResponse(BaseModel):
    baseline: ProjectionResult
    scenario: ProjectionResult | None = None
    comparison: SimulationComparison | None = None

    monte_carlo: MonteCarloBundle | None = None
    sensitivity: SensitivityResult | None = None

    warnings: list[str]
    assumptions_used: SimulationAssumptions