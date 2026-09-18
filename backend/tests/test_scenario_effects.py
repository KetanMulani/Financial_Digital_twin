import pytest

from app.schemas.scenario import (
    ExpenseChangeScenario,
    IncomeChangeScenario,
    IncomeLossScenario,
    InvestmentChangeScenario,
    LoanScenario,
    PurchaseScenario,
)
from app.simulation.scenario_effects import (
    ScenarioEffect,
    apply_recurring_effect,
    get_scenario_effect,
)


BASE_INCOME = 80_000
BASE_EXPENSES = 45_000
BASE_INVESTMENT = 10_000


def test_loan_has_no_effect_before_start():
    scenario = LoanScenario(
        amount=1_000_000,
        interest_rate=9,
        duration_months=60,
        start_month=3,
    )

    effect = get_scenario_effect(
        scenario,
        month=2,
        base_income=BASE_INCOME,
        base_expenses=BASE_EXPENSES,
    )

    assert effect == ScenarioEffect()


def test_loan_creates_cash_and_debt_at_start():
    scenario = LoanScenario(
        amount=1_000_000,
        interest_rate=9,
        duration_months=60,
        start_month=3,
    )

    effect = get_scenario_effect(
        scenario,
        month=3,
        base_income=BASE_INCOME,
        base_expenses=BASE_EXPENSES,
    )

    assert effect.cash_delta == 1_000_000
    assert effect.new_debt is not None
    assert effect.new_debt.principal == 1_000_000
    assert effect.new_debt.interest_rate == 9
    assert effect.new_debt.duration_months == 60


def test_loan_is_only_created_once():
    scenario = LoanScenario(
        amount=1_000_000,
        interest_rate=9,
        duration_months=60,
        start_month=3,
    )

    effect = get_scenario_effect(
        scenario,
        month=4,
        base_income=BASE_INCOME,
        base_expenses=BASE_EXPENSES,
    )

    assert effect.new_debt is None
    assert effect.cash_delta == 0


def test_fixed_income_change_starts_at_correct_month():
    scenario = IncomeChangeScenario(
        amount=10_000,
        start_month=3,
    )

    before = get_scenario_effect(
        scenario,
        month=2,
        base_income=BASE_INCOME,
        base_expenses=BASE_EXPENSES,
    )

    active = get_scenario_effect(
        scenario,
        month=3,
        base_income=BASE_INCOME,
        base_expenses=BASE_EXPENSES,
    )

    assert before.income_delta == 0
    assert active.income_delta == 10_000


def test_percentage_income_change():
    scenario = IncomeChangeScenario(
        percentage=10,
        start_month=1,
    )

    effect = get_scenario_effect(
        scenario,
        month=1,
        base_income=BASE_INCOME,
        base_expenses=BASE_EXPENSES,
    )

    assert effect.income_delta == 8_000


def test_expense_change_persists_after_start():
    scenario = ExpenseChangeScenario(
        amount=5_000,
        start_month=2,
    )

    effect = get_scenario_effect(
        scenario,
        month=6,
        base_income=BASE_INCOME,
        base_expenses=BASE_EXPENSES,
    )

    assert effect.expense_delta == 5_000


def test_percentage_expense_reduction():
    scenario = ExpenseChangeScenario(
        percentage=-10,
        start_month=1,
    )

    effect = get_scenario_effect(
        scenario,
        month=1,
        base_income=BASE_INCOME,
        base_expenses=BASE_EXPENSES,
    )

    assert effect.expense_delta == -4_500


def test_investment_change_overrides_contribution():
    scenario = InvestmentChangeScenario(
        new_monthly_contribution=20_000,
        start_month=2,
    )

    effect = get_scenario_effect(
        scenario,
        month=2,
        base_income=BASE_INCOME,
        base_expenses=BASE_EXPENSES,
    )

    values = apply_recurring_effect(
        effect,
        base_income=BASE_INCOME,
        base_expenses=BASE_EXPENSES,
        base_monthly_investment=BASE_INVESTMENT,
    )

    assert values.monthly_investment == 20_000


def test_financed_purchase_effect():
    scenario = PurchaseScenario(
        price=1_000_000,
        down_payment=200_000,
        financed_amount=800_000,
        interest_rate=9,
        duration_months=60,
        start_month=2,
    )

    effect = get_scenario_effect(
        scenario,
        month=2,
        base_income=BASE_INCOME,
        base_expenses=BASE_EXPENSES,
    )

    assert effect.cash_delta == -200_000
    assert effect.asset_delta == 1_000_000
    assert effect.new_debt is not None
    assert effect.new_debt.principal == 800_000
    assert effect.new_debt.source == "purchase"


def test_cash_purchase_creates_no_debt():
    scenario = PurchaseScenario(
        price=500_000,
        down_payment=500_000,
        financed_amount=0,
        start_month=1,
    )

    effect = get_scenario_effect(
        scenario,
        month=1,
        base_income=BASE_INCOME,
        base_expenses=BASE_EXPENSES,
    )

    assert effect.cash_delta == -500_000
    assert effect.asset_delta == 500_000
    assert effect.new_debt is None


def test_income_loss_is_active_for_exact_duration():
    scenario = IncomeLossScenario(
        start_month=3,
        duration_months=2,
        income_reduction=100,
    )

    month_2 = get_scenario_effect(
        scenario,
        2,
        BASE_INCOME,
        BASE_EXPENSES,
    )

    month_3 = get_scenario_effect(
        scenario,
        3,
        BASE_INCOME,
        BASE_EXPENSES,
    )

    month_4 = get_scenario_effect(
        scenario,
        4,
        BASE_INCOME,
        BASE_EXPENSES,
    )

    month_5 = get_scenario_effect(
        scenario,
        5,
        BASE_INCOME,
        BASE_EXPENSES,
    )

    assert month_2.income_delta == 0
    assert month_3.income_delta == -80_000
    assert month_4.income_delta == -80_000
    assert month_5.income_delta == 0


def test_income_cannot_become_negative():
    effect = ScenarioEffect(
        income_delta=-100_000,
    )

    values = apply_recurring_effect(
        effect,
        base_income=80_000,
        base_expenses=45_000,
        base_monthly_investment=10_000,
    )

    assert values.income == 0


def test_expenses_cannot_become_negative():
    effect = ScenarioEffect(
        expense_delta=-100_000,
    )

    values = apply_recurring_effect(
        effect,
        base_income=80_000,
        base_expenses=45_000,
        base_monthly_investment=10_000,
    )

    assert values.expenses == 0


def test_invalid_month_is_rejected():
    scenario = IncomeLossScenario(
        start_month=1,
        duration_months=2,
        income_reduction=50,
    )

    with pytest.raises(ValueError):
        get_scenario_effect(
            scenario,
            month=0,
            base_income=BASE_INCOME,
            base_expenses=BASE_EXPENSES,
        )