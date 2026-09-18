from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TwinProfileBase(BaseModel):
    monthly_income: float = Field(
        ge=0,
        description="Total monthly income",
    )

    monthly_expenses: float = Field(
        ge=0,
        description="Regular monthly expenses",
    )

    cash_savings: float = Field(
        ge=0,
        description="Current liquid savings",
    )

    investments: float = Field(
        ge=0,
        description="Current investment value",
    )

    monthly_investment: float = Field(
        default=0,
        ge=0,
        description="Amount invested every month",
    )

    existing_debt: float = Field(
        default=0,
        ge=0,
        description="Current outstanding debt",
    )

    debt_interest_rate: float = Field(
        default=0,
        ge=0,
        le=100,
        description="Annual debt interest rate in percent",
    )

    monthly_debt_payment: float = Field(
        default=0,
        ge=0,
        description="Current monthly debt payment",
    )

    financial_goal: float | None = Field(
        default=None,
        ge=0,
        description="Target net worth or financial goal",
    )


class TwinProfileUpdate(TwinProfileBase):
    pass


class TwinProfileResponse(TwinProfileBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime