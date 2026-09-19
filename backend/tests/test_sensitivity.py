from dataclasses import dataclass

import pytest
from pydantic import ValidationError

from app.schemas.scenario import (
    ExpenseChangeScenario,
    IncomeChangeScenario,
    IncomeLossScenario,
    InvestmentChangeScenario,
    LoanScenario,
    PurchaseScenario,
)
from app.schemas.simulation import (
    SensitivityConfig,
    SimulationAssumptions,
    SimulationRequest,
    SimulationResponse,
)
from app.services.simulation_service import (
    run_simulation_for_profile,
)
from app.simulation.sensitivity import (
    run_sensitivity_analysis,
)


@dataclass
class Profile:
    monthly_income: float = 100_000
    monthly_expenses: float = 50_000

    cash_savings: float = 200_000
    investments: float = 100_000
    monthly_investment: float = 10_000

    existing_debt: float = 0
    debt_interest_rate: float = 0
    monthly_debt_payment: float = 0

    financial_goal: float | None = 1_000_000


ASSUMPTIONS = SimulationAssumptions(
    annual_income_growth_rate=5,
    annual_expense_inflation_rate=5,
    annual_investment_return=10,
    annual_savings_interest_rate=3,
)


def make_config(
    **overrides,
) -> SensitivityConfig:
    values = {
        "enabled": True,
        "parameters": [
            "monthly_income",
            "monthly_expenses",
            "annual_investment_return",
        ],
        "variation_percent": 10,
    }

    values.update(
        overrides
    )

    return SensitivityConfig(
        **values
    )


def test_sensitivity_config_rejects_invalid_variation():
    with pytest.raises(
        ValidationError
    ):
        SensitivityConfig(
            enabled=True,
            parameters=[
                "monthly_income"
            ],
            variation_percent=0,
        )


def test_sensitivity_config_rejects_unknown_parameter():
    with pytest.raises(
        ValidationError
    ):
        SensitivityConfig(
            enabled=True,
            parameters=[
                "not_a_real_parameter"
            ],
            variation_percent=10,
        )


def test_analysis_returns_ranked_results():
    result = run_sensitivity_analysis(
        profile=Profile(),
        assumptions=ASSUMPTIONS,
        projection_months=60,
        config=make_config(),
    )

    assert len(
        result["ranking"]
    ) == 3

    assert (
        result[
            "most_sensitive_parameter"
        ]
        == result[
            "ranking"
        ][0][
            "parameter"
        ]
    )

    assert (
        result[
            "ranking"
        ][0][
            "normalized_impact"
        ]
        == 100
    )

    ranges = [
        item[
            "net_worth_range"
        ]
        for item in result[
            "ranking"
        ]
    ]

    assert ranges == sorted(
        ranges,
        reverse=True,
    )


def test_income_and_expense_have_expected_direction():
    result = run_sensitivity_analysis(
        profile=Profile(),
        assumptions=ASSUMPTIONS,
        projection_months=12,
        config=make_config(
            parameters=[
                "monthly_income",
                "monthly_expenses",
            ]
        ),
    )

    by_parameter = {
        item["parameter"]: item
        for item in result["ranking"]
    }

    assert (
        by_parameter[
            "monthly_income"
        ][
            "low_change"
        ]
        < 0
    )

    assert (
        by_parameter[
            "monthly_income"
        ][
            "high_change"
        ]
        > 0
    )

    assert (
        by_parameter[
            "monthly_expenses"
        ][
            "low_change"
        ]
        > 0
    )

    assert (
        by_parameter[
            "monthly_expenses"
        ][
            "high_change"
        ]
        < 0
    )


def test_analysis_does_not_mutate_inputs():
    profile = Profile()

    assumptions = (
        ASSUMPTIONS.model_copy(
            deep=True
        )
    )

    original_profile = (
        profile.__dict__.copy()
    )

    original_assumptions = (
        assumptions.model_dump()
    )

    run_sensitivity_analysis(
        profile=profile,
        assumptions=assumptions,
        projection_months=12,
        config=make_config(),
    )

    assert (
        profile.__dict__
        == original_profile
    )

    assert (
        assumptions.model_dump()
        == original_assumptions
    )


@pytest.mark.parametrize(
    "scenario",
    [
        LoanScenario(
            type="loan",
            start_month=1,
            amount=500_000,
            interest_rate=9,
            duration_months=60,
        ),
        IncomeChangeScenario(
            type="income_change",
            start_month=2,
            amount=10_000,
        ),
        ExpenseChangeScenario(
            type="expense_change",
            start_month=2,
            percentage=-10,
        ),
        InvestmentChangeScenario(
            type="investment_change",
            start_month=2,
            new_monthly_contribution=20_000,
        ),
        PurchaseScenario(
            type="purchase",
            start_month=2,
            price=500_000,
            down_payment=100_000,
            financed_amount=400_000,
            interest_rate=9,
            duration_months=60,
        ),
        IncomeLossScenario(
            type="income_loss",
            start_month=2,
            duration_months=3,
            income_reduction=50,
        ),
    ],
)
def test_all_scenarios_work_with_sensitivity(
    scenario,
):
    result = run_sensitivity_analysis(
        profile=Profile(),
        assumptions=ASSUMPTIONS,
        projection_months=12,
        config=make_config(
            parameters=[
                "monthly_income"
            ]
        ),
        scenario=scenario,
    )

    assert len(
        result["ranking"]
    ) == 1

    assert (
        result[
            "ranking"
        ][0][
            "parameter"
        ]
        == "monthly_income"
    )


def test_non_negative_parameter_is_bounded():
    result = run_sensitivity_analysis(
        profile=Profile(
            cash_savings=100
        ),
        assumptions=ASSUMPTIONS,
        projection_months=1,
        config=make_config(
            parameters=[
                "cash_savings"
            ],
            variation_percent=100,
        ),
    )

    item = result[
        "ranking"
    ][0]

    assert item["low_value"] == 0
    assert item["high_value"] == 200


def test_service_skips_sensitivity_when_disabled():
    request = SimulationRequest(
        projection_months=12,
        assumptions=ASSUMPTIONS,
    )

    response = (
        run_simulation_for_profile(
            profile=Profile(),
            request=request,
        )
    )

    assert (
        response[
            "sensitivity"
        ]
        is None
    )


def test_service_runs_sensitivity_and_validates():
    request = SimulationRequest(
        projection_months=12,
        assumptions=ASSUMPTIONS,
        scenario={
            "type": "income_loss",
            "start_month": 2,
            "duration_months": 2,
            "income_reduction": 50,
        },
        sensitivity={
            "enabled": True,
            "parameters": [
                "monthly_income",
                "monthly_expenses",
                "annual_investment_return",
            ],
            "variation_percent": 10,
        },
    )

    response = (
        run_simulation_for_profile(
            profile=Profile(),
            request=request,
        )
    )

    validated_response = (
        SimulationResponse.model_validate(
            response
        )
    )

    assert (
        validated_response.sensitivity
        is not None
    )

    assert len(
        validated_response
        .sensitivity
        .ranking
    ) == 3


def test_monte_carlo_and_sensitivity_can_run_together():
    request = SimulationRequest(
        projection_months=12,
        assumptions=ASSUMPTIONS,
        monte_carlo={
            "enabled": True,
            "simulations": 100,
            "seed": 42,
            "investment_return_std": 5,
            "income_growth_std": 2,
            "expense_inflation_std": 2,
        },
        sensitivity={
            "enabled": True,
            "parameters": [
                "monthly_income"
            ],
            "variation_percent": 10,
        },
    )

    response = (
        run_simulation_for_profile(
            profile=Profile(),
            request=request,
        )
    )

    assert (
        response[
            "monte_carlo"
        ]
        is not None
    )

    assert (
        response[
            "sensitivity"
        ]
        is not None
    )