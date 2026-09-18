from typing import Literal

from pydantic import BaseModel, Field


class LoanScenarioRequest(BaseModel):
    amount: float = Field(gt=0)
    interest_rate: float = Field(ge=0)
    duration_months: int = Field(gt=0)


class SimulationRequest(BaseModel):
    type: Literal["baseline", "loan"] = "baseline"

    months: int = Field(default=60, gt=0, le=120)

    annual_investment_return: float = Field(
        default=0.10,
        ge=-1,
    )

    annual_inflation: float = Field(
        default=0.05,
        ge=-1,
    )

    loan: LoanScenarioRequest | None = None

    monte_carlo: bool = False

    simulations: int = Field(
        default=1000,
        gt=0,
        le=10000,
    )


class SimulationResponse(BaseModel):
    baseline: dict
    scenario: dict | None = None
    comparison: dict | None = None
    monte_carlo: dict | None = None