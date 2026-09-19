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
    MonteCarloConfig,
    SimulationAssumptions,
    SimulationRequest,
)
from app.services.simulation_service import (
    run_simulation_for_profile,
)
from app.simulation.monte_carlo import (
    compare_monte_carlo,
    run_monte_carlo,
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


CONFIG = MonteCarloConfig(
    enabled=True,
    simulations=200,
    seed=42,
    investment_return_std=5,
    income_growth_std=2,
    expense_inflation_std=2,
)


def test_same_seed_produces_same_results():
    first = run_monte_carlo(
        profile=Profile(),
        base_assumptions=ASSUMPTIONS,
        projection_months=60,
        config=CONFIG,
    )

    second = run_monte_carlo(
        profile=Profile(),
        base_assumptions=ASSUMPTIONS,
        projection_months=60,
        config=CONFIG,
    )

    assert first == second


def test_correct_simulation_count():
    result = run_monte_carlo(
        profile=Profile(),
        base_assumptions=ASSUMPTIONS,
        projection_months=60,
        config=CONFIG,
    )

    assert result["simulations"] == 200
    assert result["seed"] == 42


def test_percentiles_are_ordered():
    result = run_monte_carlo(
        profile=Profile(),
        base_assumptions=ASSUMPTIONS,
        projection_months=60,
        config=CONFIG,
    )

    net_worth = result[
        "final_net_worth"
    ]

    assert (
        net_worth["p10"]
        <= net_worth["p50"]
        <= net_worth["p90"]
    )


def test_probabilities_are_valid():
    result = run_monte_carlo(
        profile=Profile(),
        base_assumptions=ASSUMPTIONS,
        projection_months=60,
        config=CONFIG,
    )

    goal_probability = result[
        "probability_of_reaching_goal"
    ]

    assert goal_probability is not None
    assert 0 <= goal_probability <= 100

    assert (
        0
        <= result[
            "probability_of_cash_depletion"
        ]
        <= 100
    )

    assert (
        0
        <= result[
            "probability_of_unfunded_deficit"
        ]
        <= 100
    )


def test_goal_probability_is_none_without_goal():
    profile = Profile(
        financial_goal=None
    )

    result = run_monte_carlo(
        profile=profile,
        base_assumptions=ASSUMPTIONS,
        projection_months=60,
        config=CONFIG,
    )

    assert (
        result[
            "probability_of_reaching_goal"
        ]
        is None
    )


def test_zero_standard_deviation_is_deterministic():
    deterministic_config = MonteCarloConfig(
        enabled=True,
        simulations=100,
        seed=42,
        investment_return_std=0,
        income_growth_std=0,
        expense_inflation_std=0,
    )

    result = run_monte_carlo(
        profile=Profile(),
        base_assumptions=ASSUMPTIONS,
        projection_months=12,
        config=deterministic_config,
    )

    net_worth = result[
        "final_net_worth"
    ]

    assert net_worth["p10"] == net_worth["p50"]
    assert net_worth["p50"] == net_worth["p90"]
    assert net_worth["minimum"] == net_worth["maximum"]


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
def test_all_scenarios_work_with_monte_carlo(
    scenario,
):
    result = run_monte_carlo(
        profile=Profile(),
        base_assumptions=ASSUMPTIONS,
        projection_months=12,
        config=CONFIG,
        scenario=scenario,
    )

    assert result["simulations"] == 200

    assert (
        result["final_net_worth"]["p10"]
        <= result["final_net_worth"]["p50"]
        <= result["final_net_worth"]["p90"]
    )


def test_monte_carlo_comparison():
    baseline = run_monte_carlo(
        profile=Profile(),
        base_assumptions=ASSUMPTIONS,
        projection_months=24,
        config=CONFIG,
    )

    scenario = IncomeLossScenario(
        type="income_loss",
        start_month=1,
        duration_months=3,
        income_reduction=100,
    )

    scenario_result = run_monte_carlo(
        profile=Profile(),
        base_assumptions=ASSUMPTIONS,
        projection_months=24,
        config=CONFIG,
        scenario=scenario,
    )

    comparison = compare_monte_carlo(
        baseline_result=baseline,
        scenario_result=scenario_result,
    )

    assert (
        comparison[
            "net_worth_p50_difference"
        ]
        <= 0
    )


def test_service_runs_monte_carlo():
    request = SimulationRequest(
        projection_months=12,
        assumptions=ASSUMPTIONS,
        scenario={
            "type": "income_loss",
            "start_month": 2,
            "duration_months": 2,
            "income_reduction": 50,
        },
        monte_carlo={
            "enabled": True,
            "simulations": 100,
            "seed": 42,
            "investment_return_std": 5,
            "income_growth_std": 2,
            "expense_inflation_std": 2,
        },
    )

    response = run_simulation_for_profile(
        profile=Profile(),
        request=request,
    )

    assert response["monte_carlo"] is not None

    assert (
        response["monte_carlo"]["baseline"]
        is not None
    )

    assert (
        response["monte_carlo"]["scenario"]
        is not None
    )

    assert (
        response["monte_carlo"]["comparison"]
        is not None
    )


def test_service_skips_monte_carlo_when_disabled():
    request = SimulationRequest(
        projection_months=12,
        assumptions=ASSUMPTIONS,
        scenario=None,
    )

    response = run_simulation_for_profile(
        profile=Profile(),
        request=request,
    )

    assert response["monte_carlo"] is None