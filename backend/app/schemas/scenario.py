from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter, model_validator


class ScenarioBase(BaseModel):
    start_month: int = Field(ge=1, le=600)

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )


class LoanScenario(ScenarioBase):
    type: Literal["loan"]

    amount: float = Field(gt=0)
    interest_rate: float = Field(ge=0, le=100)
    duration_months: int = Field(ge=1, le=600)


class IncomeChangeScenario(ScenarioBase):
    type: Literal["income_change"]

    amount: float | None = None
    percentage: float | None = Field(default=None, ge=-100, le=1000)

    @model_validator(mode="after")
    def validate_change(self):
        if (self.amount is None) == (self.percentage is None):
            raise ValueError("Provide exactly one of amount or percentage.")

        if self.amount == 0 or self.percentage == 0:
            raise ValueError("Change cannot be zero.")

        return self


class ExpenseChangeScenario(ScenarioBase):
    type: Literal["expense_change"]

    amount: float | None = None
    percentage: float | None = Field(default=None, ge=-100, le=1000)

    @model_validator(mode="after")
    def validate_change(self):
        if (self.amount is None) == (self.percentage is None):
            raise ValueError("Provide exactly one of amount or percentage.")

        if self.amount == 0 or self.percentage == 0:
            raise ValueError("Change cannot be zero.")

        return self


class InvestmentChangeScenario(ScenarioBase):
    type: Literal["investment_change"]

    new_monthly_contribution: float = Field(ge=0)


class PurchaseScenario(ScenarioBase):
    type: Literal["purchase"]

    price: float = Field(gt=0)
    down_payment: float = Field(ge=0)
    financed_amount: float = Field(ge=0)

    @model_validator(mode="after")
    def validate_purchase(self):
        if self.down_payment > self.price:
            raise ValueError("Down payment cannot exceed purchase price.")

        if abs(
            (self.down_payment + self.financed_amount) - self.price
        ) > 0.01:
            raise ValueError(
                "Down payment plus financed amount must equal purchase price."
            )

        return self


class IncomeLossScenario(ScenarioBase):
    type: Literal["income_loss"]

    duration_months: int = Field(ge=1, le=600)
    income_reduction: float = Field(gt=0, le=100)


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


class ScenarioPayload(BaseModel):
    scenario: Scenario