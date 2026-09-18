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


def test_valid_loan_scenario():
    scenario = LoanScenario(
        type="loan",
        start_month=1,
        amount=1_000_000,
        interest_rate=9.5,
        duration_months=60,
    )

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


def test_valid_income_change_with_amount():
    scenario = IncomeChangeScenario(
        type="income_change",
        start_month=2,
        amount=10_000,
    )

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


def test_expense_change():
    scenario = ExpenseChangeScenario(
        type="expense_change",
        start_month=1,
        percentage=-10,
    )

    assert scenario.percentage == -10


def test_investment_change():
    scenario = InvestmentChangeScenario(
        type="investment_change",
        start_month=3,
        new_monthly_contribution=20_000,
    )

    assert scenario.new_monthly_contribution == 20_000


def test_purchase_valid():
    scenario = PurchaseScenario(
        type="purchase",
        start_month=1,
        price=1_000_000,
        down_payment=200_000,
        financed_amount=800_000,
    )

    assert scenario.price == 1_000_000


def test_purchase_down_payment_cannot_exceed_price():
    with pytest.raises(ValidationError):
        PurchaseScenario(
            type="purchase",
            start_month=1,
            price=1_000_000,
            down_payment=1_100_000,
            financed_amount=0,
        )


def test_purchase_amounts_must_match():
    with pytest.raises(ValidationError):
        PurchaseScenario(
            type="purchase",
            start_month=1,
            price=1_000_000,
            down_payment=200_000,
            financed_amount=700_000,
        )


def test_income_loss():
    scenario = IncomeLossScenario(
        type="income_loss",
        start_month=2,
        duration_months=6,
        income_reduction=50,
    )

    assert scenario.duration_months == 6
    assert scenario.income_reduction == 50


def test_income_loss_cannot_exceed_100_percent():
    with pytest.raises(ValidationError):
        IncomeLossScenario(
            type="income_loss",
            start_month=1,
            duration_months=6,
            income_reduction=101,
        )


def test_discriminated_union_loan():
    payload = {
        "type": "loan",
        "start_month": 1,
        "amount": 500_000,
        "interest_rate": 9,
        "duration_months": 60,
    }

    scenario = scenario_adapter.validate_python(payload)

    assert isinstance(scenario, LoanScenario)


def test_discriminated_union_income_loss():
    payload = {
        "type": "income_loss",
        "start_month": 2,
        "duration_months": 3,
        "income_reduction": 50,
    }

    scenario = scenario_adapter.validate_python(payload)

    assert isinstance(scenario, IncomeLossScenario)


def test_unknown_scenario_type():
    payload = {
        "type": "something_else",
        "start_month": 1,
    }

    with pytest.raises(ValidationError):
        scenario_adapter.validate_python(payload)


def test_scenario_payload():
    payload = ScenarioPayload(
        scenario={
            "type": "investment_change",
            "start_month": 1,
            "new_monthly_contribution": 15_000,
        }
    )

    assert isinstance(payload.scenario, InvestmentChangeScenario)


def test_unknown_fields_are_rejected():
    with pytest.raises(ValidationError):
        scenario_adapter.validate_python(
            {
                "type": "loan",
                "amount": 1_000_000,
                "interest_rate": 9,
                "duration_months": 60,
                "random_field": "should not be accepted",
            }
        )


def test_purchase_valid():
    scenario = PurchaseScenario(
        type="purchase",
        start_month=1,
        price=1_000_000,
        down_payment=200_000,
        financed_amount=800_000,
        interest_rate=9,
        duration_months=60,
    )

    assert scenario.price == 1_000_000


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


def test_cash_purchase_does_not_require_financing_details():
    scenario = PurchaseScenario(
        type="purchase",
        start_month=1,
        price=500_000,
        down_payment=500_000,
        financed_amount=0,
    )

    assert scenario.interest_rate is None
    assert scenario.duration_months is None