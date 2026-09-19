from dataclasses import dataclass

import pytest

from app.schemas.scenario import (
    ExpenseChangeScenario,
    IncomeChangeScenario,
    IncomeLossScenario,
    InvestmentChangeScenario,
    LoanScenario,
    PurchaseScenario,
)
from app.schemas.simulation import (
    SimulationAssumptions,
    SimulationRequest,
)
from app.services.simulation_service import (
    run_simulation_for_profile,
)
from app.simulation.engine import (
    calculate_emi,
    project_finances,
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


ZERO_ASSUMPTIONS = SimulationAssumptions(
    annual_income_growth_rate=0,
    annual_expense_inflation_rate=0,
    annual_investment_return=0,
    annual_savings_interest_rate=0,
)


def run_projection(
    scenario=None,
    months=12,
    profile=None,
):
    return project_finances(
        profile=profile or Profile(),
        assumptions=ZERO_ASSUMPTIONS,
        projection_months=months,
        scenario=scenario,
    )


def test_zero_growth_baseline():
    result = run_projection()

    summary = result["final_summary"]

    assert (
        summary["final_cash_savings"]
        == 680_000
    )

    assert (
        summary["final_investment_value"]
        == 220_000
    )

    assert (
        summary["final_net_worth"]
        == 900_000
    )


def test_engine_is_deterministic():
    first = run_projection()
    second = run_projection()

    assert first == second


def test_loan_adds_cash_and_debt():
    loan = LoanScenario(
        type="loan",
        amount=120_000,
        interest_rate=0,
        duration_months=12,
        start_month=1,
    )

    baseline = run_projection(months=1)

    scenario_result = run_projection(
        scenario=loan,
        months=1,
    )

    assert (
        scenario_result["timeline"][0][
            "debt_payment"
        ]
        == 10_000
    )

    # A zero-interest loan does not cause an
    # artificial immediate net-worth loss.
    assert (
        scenario_result["final_summary"][
            "final_net_worth"
        ]
        == baseline["final_summary"][
            "final_net_worth"
        ]
    )


def test_loan_respects_start_month():
    loan = LoanScenario(
        type="loan",
        amount=120_000,
        interest_rate=0,
        duration_months=12,
        start_month=3,
    )

    result = run_projection(
        scenario=loan,
        months=3,
    )

    assert (
        result["timeline"][0][
            "remaining_debt"
        ]
        == 0
    )

    assert (
        result["timeline"][1][
            "remaining_debt"
        ]
        == 0
    )

    assert (
        result["timeline"][2][
            "remaining_debt"
        ]
        == 110_000
    )


def test_income_change_reaches_engine():
    scenario = IncomeChangeScenario(
        type="income_change",
        amount=20_000,
        start_month=2,
    )

    result = run_projection(
        scenario=scenario,
        months=2,
    )

    assert (
        result["timeline"][0]["income"]
        == 100_000
    )

    assert (
        result["timeline"][1]["income"]
        == 120_000
    )


def test_expense_change_reaches_engine():
    scenario = ExpenseChangeScenario(
        type="expense_change",
        percentage=-10,
        start_month=2,
    )

    result = run_projection(
        scenario=scenario,
        months=2,
    )

    assert (
        result["timeline"][0]["expenses"]
        == 50_000
    )

    assert (
        result["timeline"][1]["expenses"]
        == 45_000
    )


def test_investment_change_reaches_engine():
    scenario = InvestmentChangeScenario(
        type="investment_change",
        new_monthly_contribution=25_000,
        start_month=2,
    )

    result = run_projection(
        scenario=scenario,
        months=2,
    )

    assert (
        result["timeline"][0][
            "investment_contribution"
        ]
        == 10_000
    )

    assert (
        result["timeline"][1][
            "investment_contribution"
        ]
        == 25_000
    )


def test_purchase_tracks_asset_and_debt():
    purchase = PurchaseScenario(
        type="purchase",
        price=300_000,
        down_payment=100_000,
        financed_amount=200_000,
        interest_rate=0,
        duration_months=20,
        start_month=1,
    )

    result = run_projection(
        scenario=purchase,
        months=1,
    )

    point = result["timeline"][0]

    assert (
        point["scenario_asset_value"]
        == 300_000
    )

    assert point["remaining_debt"] == 190_000
    assert point["debt_payment"] == 10_000


def test_income_loss_ends_after_duration():
    scenario = IncomeLossScenario(
        type="income_loss",
        start_month=2,
        duration_months=2,
        income_reduction=50,
    )

    result = run_projection(
        scenario=scenario,
        months=4,
    )

    incomes = [
        point["income"]
        for point in result["timeline"]
    ]

    assert incomes == [
        100_000,
        50_000,
        50_000,
        100_000,
    ]


def test_cash_cannot_become_negative():
    profile = Profile(
        monthly_income=0,
        monthly_expenses=100_000,
        cash_savings=10_000,
        investments=0,
        monthly_investment=0,
        financial_goal=None,
    )

    result = run_projection(
        months=1,
        profile=profile,
    )

    summary = result["final_summary"]

    assert summary["final_cash_savings"] == 0

    assert (
        summary["final_unfunded_deficit"]
        == 90_000
    )

    assert (
        summary["final_net_worth"]
        == -90_000
    )


def test_existing_debt_accrues_and_reduces():
    profile = Profile(
        existing_debt=120_000,
        debt_interest_rate=12,
        monthly_debt_payment=12_000,
    )

    result = run_projection(
        months=1,
        profile=profile,
    )

    assert (
        result["timeline"][0][
            "remaining_debt"
        ]
        == 109_200
    )

    assert (
        result["final_summary"][
            "total_interest_paid"
        ]
        == 1_200
    )


def test_existing_debt_grows_when_no_payment():
    profile = Profile(
        existing_debt=120_000,
        debt_interest_rate=12,
        monthly_debt_payment=0,
    )

    result = run_projection(
        months=1,
        profile=profile,
    )

    assert (
        result["timeline"][0][
            "remaining_debt"
        ]
        == 121_200
    )


def test_service_returns_comparison():
    request = SimulationRequest(
        projection_months=12,
        assumptions=ZERO_ASSUMPTIONS,
        scenario={
            "type": "income_loss",
            "start_month": 1,
            "duration_months": 1,
            "income_reduction": 100,
        },
    )

    response = run_simulation_for_profile(
        profile=Profile(),
        request=request,
    )

    expected_difference = (
        response["scenario"]["final_summary"][
            "final_net_worth"
        ]
        - response["baseline"]["final_summary"][
            "final_net_worth"
        ]
    )

    assert (
        response["comparison"][
            "net_worth_difference"
        ]
        == expected_difference
    )


@pytest.mark.parametrize(
    (
        "principal",
        "rate",
        "months",
        "expected",
    ),
    [
        (120_000, 0, 12, 10_000),
        (0, 10, 12, 0),
    ],
)
def test_emi_edge_cases(
    principal,
    rate,
    months,
    expected,
):
    assert (
        calculate_emi(
            principal,
            rate,
            months,
        )
        == expected
    )