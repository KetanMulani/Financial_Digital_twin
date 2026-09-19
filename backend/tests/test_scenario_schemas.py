import pytest
from pydantic import ValidationError

from app.schemas.scenario import (
    ExpenseChangeScenario,
    IncomeChangeScenario,
    IncomeLossScenario,
    InvestmentChangeScenario,
    LoanScenario,
    PurchaseScenario,
    ScenarioPayload,
    scenario_adapter,
)


# ============================================================
# LOAN SCENARIO
# ============================================================


def test_valid_loan_scenario():
    scenario = LoanScenario(
        type="loan",
        start_month=1,
        amount=1_000_000,
        interest_rate=9.5,
        duration_months=60,
    )

    assert scenario.type == "loan"
    assert scenario.start_month == 1
    assert scenario.amount == 1_000_000
    assert scenario.interest_rate == 9.5
    assert scenario.duration_months == 60


def test_invalid_loan_amount():
    with pytest.raises(ValidationError):
        LoanScenario(
            type="loan",
            start_month=1,
            amount=-100_000,
            interest_rate=9.5,
            duration_months=60,
        )


def test_invalid_loan_duration():
    with pytest.raises(ValidationError):
        LoanScenario(
            type="loan",
            start_month=1,
            amount=100_000,
            interest_rate=9.5,
            duration_months=0,
        )


def test_invalid_loan_interest_rate():
    with pytest.raises(ValidationError):
        LoanScenario(
            type="loan",
            start_month=1,
            amount=100_000,
            interest_rate=101,
            duration_months=60,
        )


def test_invalid_scenario_start_month():
    with pytest.raises(ValidationError):
        LoanScenario(
            type="loan",
            start_month=0,
            amount=100_000,
            interest_rate=9,
            duration_months=60,
        )


# ============================================================
# INCOME-CHANGE SCENARIO
# ============================================================


def test_valid_income_change_with_amount():
    scenario = IncomeChangeScenario(
        type="income_change",
        start_month=2,
        amount=10_000,
    )

    assert scenario.type == "income_change"
    assert scenario.start_month == 2
    assert scenario.amount == 10_000
    assert scenario.percentage is None


def test_valid_income_change_with_percentage():
    scenario = IncomeChangeScenario(
        type="income_change",
        start_month=2,
        percentage=10,
    )

    assert scenario.percentage == 10
    assert scenario.amount is None


def test_income_change_requires_exactly_one_value():
    with pytest.raises(ValidationError):
        IncomeChangeScenario(
            type="income_change",
            start_month=1,
        )


def test_income_change_rejects_amount_and_percentage_together():
    with pytest.raises(ValidationError):
        IncomeChangeScenario(
            type="income_change",
            start_month=1,
            amount=10_000,
            percentage=10,
        )


def test_income_change_cannot_be_zero():
    with pytest.raises(ValidationError):
        IncomeChangeScenario(
            type="income_change",
            start_month=1,
            amount=0,
        )


def test_income_reduction_cannot_exceed_100_percent():
    with pytest.raises(ValidationError):
        IncomeChangeScenario(
            type="income_change",
            start_month=1,
            percentage=-101,
        )


# ============================================================
# EXPENSE-CHANGE SCENARIO
# ============================================================


def test_valid_expense_change_with_amount():
    scenario = ExpenseChangeScenario(
        type="expense_change",
        start_month=1,
        amount=5_000,
    )

    assert scenario.type == "expense_change"
    assert scenario.amount == 5_000
    assert scenario.percentage is None


def test_valid_expense_change_with_percentage():
    scenario = ExpenseChangeScenario(
        type="expense_change",
        start_month=1,
        percentage=-10,
    )

    assert scenario.percentage == -10
    assert scenario.amount is None


def test_expense_change_requires_exactly_one_value():
    with pytest.raises(ValidationError):
        ExpenseChangeScenario(
            type="expense_change",
            start_month=1,
        )


def test_expense_change_rejects_amount_and_percentage_together():
    with pytest.raises(ValidationError):
        ExpenseChangeScenario(
            type="expense_change",
            start_month=1,
            amount=5_000,
            percentage=10,
        )


def test_expense_change_cannot_be_zero():
    with pytest.raises(ValidationError):
        ExpenseChangeScenario(
            type="expense_change",
            start_month=1,
            percentage=0,
        )


# ============================================================
# INVESTMENT-CHANGE SCENARIO
# ============================================================


def test_valid_investment_change():
    scenario = InvestmentChangeScenario(
        type="investment_change",
        start_month=3,
        new_monthly_contribution=20_000,
    )

    assert scenario.type == "investment_change"
    assert scenario.start_month == 3
    assert scenario.new_monthly_contribution == 20_000


def test_investment_contribution_cannot_be_negative():
    with pytest.raises(ValidationError):
        InvestmentChangeScenario(
            type="investment_change",
            start_month=3,
            new_monthly_contribution=-1,
        )


def test_investment_contribution_can_be_zero():
    scenario = InvestmentChangeScenario(
        type="investment_change",
        start_month=3,
        new_monthly_contribution=0,
    )

    assert scenario.new_monthly_contribution == 0


# ============================================================
# PURCHASE SCENARIO
# ============================================================


def test_valid_financed_purchase():
    scenario = PurchaseScenario(
        type="purchase",
        start_month=1,
        price=1_000_000,
        down_payment=200_000,
        financed_amount=800_000,
        interest_rate=9,
        duration_months=60,
    )

    assert scenario.type == "purchase"
    assert scenario.price == 1_000_000
    assert scenario.down_payment == 200_000
    assert scenario.financed_amount == 800_000
    assert scenario.interest_rate == 9
    assert scenario.duration_months == 60


def test_valid_cash_purchase():
    scenario = PurchaseScenario(
        type="purchase",
        start_month=1,
        price=500_000,
        down_payment=500_000,
        financed_amount=0,
    )

    assert scenario.price == 500_000
    assert scenario.down_payment == 500_000
    assert scenario.financed_amount == 0
    assert scenario.interest_rate is None
    assert scenario.duration_months is None


def test_purchase_down_payment_cannot_exceed_price():
    with pytest.raises(ValidationError):
        PurchaseScenario(
            type="purchase",
            start_month=1,
            price=1_000_000,
            down_payment=1_100_000,
            financed_amount=0,
        )


def test_purchase_amounts_must_match_price():
    with pytest.raises(ValidationError):
        PurchaseScenario(
            type="purchase",
            start_month=1,
            price=1_000_000,
            down_payment=200_000,
            financed_amount=700_000,
            interest_rate=9,
            duration_months=60,
        )


def test_financed_purchase_requires_interest_rate():
    with pytest.raises(ValidationError):
        PurchaseScenario(
            type="purchase",
            start_month=1,
            price=1_000_000,
            down_payment=200_000,
            financed_amount=800_000,
            duration_months=60,
        )


def test_financed_purchase_requires_duration():
    with pytest.raises(ValidationError):
        PurchaseScenario(
            type="purchase",
            start_month=1,
            price=1_000_000,
            down_payment=200_000,
            financed_amount=800_000,
            interest_rate=9,
        )


def test_cash_purchase_rejects_financing_details():
    with pytest.raises(ValidationError):
        PurchaseScenario(
            type="purchase",
            start_month=1,
            price=500_000,
            down_payment=500_000,
            financed_amount=0,
            interest_rate=9,
            duration_months=60,
        )


def test_purchase_price_must_be_positive():
    with pytest.raises(ValidationError):
        PurchaseScenario(
            type="purchase",
            start_month=1,
            price=0,
            down_payment=0,
            financed_amount=0,
        )


# ============================================================
# INCOME-LOSS SCENARIO
# ============================================================


def test_valid_income_loss():
    scenario = IncomeLossScenario(
        type="income_loss",
        start_month=2,
        duration_months=6,
        income_reduction=50,
    )

    assert scenario.type == "income_loss"
    assert scenario.start_month == 2
    assert scenario.duration_months == 6
    assert scenario.income_reduction == 50


def test_complete_income_loss_is_allowed():
    scenario = IncomeLossScenario(
        type="income_loss",
        start_month=2,
        duration_months=6,
        income_reduction=100,
    )

    assert scenario.income_reduction == 100


def test_income_loss_cannot_exceed_100_percent():
    with pytest.raises(ValidationError):
        IncomeLossScenario(
            type="income_loss",
            start_month=1,
            duration_months=6,
            income_reduction=101,
        )


def test_income_loss_reduction_must_be_positive():
    with pytest.raises(ValidationError):
        IncomeLossScenario(
            type="income_loss",
            start_month=1,
            duration_months=6,
            income_reduction=0,
        )


def test_income_loss_duration_must_be_positive():
    with pytest.raises(ValidationError):
        IncomeLossScenario(
            type="income_loss",
            start_month=1,
            duration_months=0,
            income_reduction=50,
        )


# ============================================================
# DISCRIMINATED UNION
# ============================================================


def test_discriminated_union_loan():
    payload = {
        "type": "loan",
        "start_month": 1,
        "amount": 500_000,
        "interest_rate": 9,
        "duration_months": 60,
    }

    scenario = scenario_adapter.validate_python(
        payload
    )

    assert isinstance(
        scenario,
        LoanScenario,
    )


def test_discriminated_union_income_loss():
    payload = {
        "type": "income_loss",
        "start_month": 2,
        "duration_months": 3,
        "income_reduction": 50,
    }

    scenario = scenario_adapter.validate_python(
        payload
    )

    assert isinstance(
        scenario,
        IncomeLossScenario,
    )


def test_discriminated_union_financed_purchase():
    payload = {
        "type": "purchase",
        "start_month": 1,
        "price": 1_000_000,
        "down_payment": 200_000,
        "financed_amount": 800_000,
        "interest_rate": 9,
        "duration_months": 60,
    }

    scenario = scenario_adapter.validate_python(
        payload
    )

    assert isinstance(
        scenario,
        PurchaseScenario,
    )


def test_unknown_scenario_type():
    payload = {
        "type": "something_else",
        "start_month": 1,
    }

    with pytest.raises(ValidationError):
        scenario_adapter.validate_python(
            payload
        )


def test_scenario_payload():
    payload = ScenarioPayload(
        scenario={
            "type": "investment_change",
            "start_month": 1,
            "new_monthly_contribution": 15_000,
        }
    )

    assert isinstance(
        payload.scenario,
        InvestmentChangeScenario,
    )


def test_unknown_fields_are_rejected():
    with pytest.raises(ValidationError):
        scenario_adapter.validate_python(
            {
                "type": "loan",
                "start_month": 1,
                "amount": 1_000_000,
                "interest_rate": 9,
                "duration_months": 60,
                "random_field": (
                    "should not be accepted"
                ),
            }
        )