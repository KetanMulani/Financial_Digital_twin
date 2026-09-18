from typing import Annotated, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    TypeAdapter,
    model_validator,
)


# ============================================================
# BASE SCENARIO
# ============================================================

class ScenarioBase(BaseModel):
    """
    Fields shared by every financial scenario.
    """

    start_month: int = Field(
        default=1,
        ge=1,
        le=600,
        description="Month in which the scenario begins",
    )

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )


# ============================================================
# LOAN
# ============================================================

class LoanScenario(ScenarioBase):
    """
    A new loan taken by the user.
    """

    type: Literal["loan"] = "loan"

    amount: float = Field(
        gt=0,
        description="Principal amount borrowed",
    )

    interest_rate: float = Field(
        ge=0,
        le=100,
        description="Annual loan interest rate in percent",
    )

    duration_months: int = Field(
        ge=1,
        le=600,
        description="Loan repayment duration in months",
    )


# ============================================================
# INCOME CHANGE
# ============================================================

class IncomeChangeScenario(ScenarioBase):
    """
    A permanent income increase or decrease.

    Provide either a fixed amount or a percentage,
    but not both.
    """

    type: Literal["income_change"] = "income_change"

    amount: float | None = Field(
        default=None,
        description="Fixed monthly income change",
    )

    percentage: float | None = Field(
        default=None,
        ge=-100,
        le=1000,
        description="Percentage change in monthly income",
    )

    @model_validator(mode="after")
    def validate_change(self):
        amount_provided = self.amount is not None
        percentage_provided = self.percentage is not None

        if amount_provided == percentage_provided:
            raise ValueError(
                "Provide exactly one of amount or percentage."
            )

        if self.amount == 0 or self.percentage == 0:
            raise ValueError(
                "Income change cannot be zero."
            )

        return self


# ============================================================
# EXPENSE CHANGE
# ============================================================

class ExpenseChangeScenario(ScenarioBase):
    """
    A permanent expense increase or decrease.

    Provide either a fixed amount or a percentage,
    but not both.
    """

    type: Literal["expense_change"] = "expense_change"

    amount: float | None = Field(
        default=None,
        description="Fixed monthly expense change",
    )

    percentage: float | None = Field(
        default=None,
        ge=-100,
        le=1000,
        description="Percentage change in monthly expenses",
    )

    @model_validator(mode="after")
    def validate_change(self):
        amount_provided = self.amount is not None
        percentage_provided = self.percentage is not None

        if amount_provided == percentage_provided:
            raise ValueError(
                "Provide exactly one of amount or percentage."
            )

        if self.amount == 0 or self.percentage == 0:
            raise ValueError(
                "Expense change cannot be zero."
            )

        return self


# ============================================================
# INVESTMENT CHANGE
# ============================================================

class InvestmentChangeScenario(ScenarioBase):
    """
    A change in the monthly investment contribution.
    """

    type: Literal["investment_change"] = "investment_change"

    new_monthly_contribution: float = Field(
        ge=0,
        description="New monthly investment contribution",
    )


# ============================================================
# PURCHASE
# ============================================================

class PurchaseScenario(ScenarioBase):
    """
    A purchase made using a down payment and optional financing.
    """

    type: Literal["purchase"] = "purchase"

    price: float = Field(
        gt=0,
        description="Total purchase price",
    )

    down_payment: float = Field(
        ge=0,
        description="Amount paid immediately from savings",
    )

    financed_amount: float = Field(
        ge=0,
        description="Amount financed through debt",
    )

    interest_rate: float | None = Field(
        default=None,
        ge=0,
        le=100,
        description="Annual interest rate for financed amount",
    )

    duration_months: int | None = Field(
        default=None,
        ge=1,
        le=600,
        description="Financing duration in months",
    )

    @model_validator(mode="after")
    def validate_purchase(self):
        if self.down_payment > self.price:
            raise ValueError(
                "Down payment cannot exceed purchase price."
            )

        funded_amount = (
            self.down_payment + self.financed_amount
        )

        if abs(funded_amount - self.price) > 0.01:
            raise ValueError(
                "Down payment plus financed amount "
                "must equal purchase price."
            )

        has_interest_rate = self.interest_rate is not None
        has_duration = self.duration_months is not None

        if self.financed_amount > 0:
            if not has_interest_rate or not has_duration:
                raise ValueError(
                    "A financed purchase requires "
                    "interest_rate and duration_months."
                )

        elif has_interest_rate or has_duration:
            raise ValueError(
                "Financing details must not be provided "
                "when financed_amount is zero."
            )

        return self


# ============================================================
# INCOME LOSS
# ============================================================

class IncomeLossScenario(ScenarioBase):
    """
    A temporary partial or complete loss of income.
    """

    type: Literal["income_loss"] = "income_loss"

    duration_months: int = Field(
        ge=1,
        le=600,
        description="Number of months income is reduced",
    )

    income_reduction: float = Field(
        gt=0,
        le=100,
        description="Percentage of monthly income lost",
    )


# ============================================================
# DISCRIMINATED UNION
# ============================================================

Scenario = Annotated[
    (
        LoanScenario
        | IncomeChangeScenario
        | ExpenseChangeScenario
        | InvestmentChangeScenario
        | PurchaseScenario
        | IncomeLossScenario
    ),
    Field(discriminator="type"),
]


scenario_adapter = TypeAdapter(Scenario)


# ============================================================
# API WRAPPER
# ============================================================

class ScenarioPayload(BaseModel):
    """
    Request wrapper for an API endpoint receiving a scenario.
    """

    scenario: Scenario