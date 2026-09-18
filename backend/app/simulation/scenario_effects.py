from dataclasses import dataclass

from app.schemas.scenario import (
    ExpenseChangeScenario,
    IncomeChangeScenario,
    IncomeLossScenario,
    InvestmentChangeScenario,
    LoanScenario,
    PurchaseScenario,
    Scenario,
)


@dataclass(frozen=True)
class NewDebtEffect:
    """
    A debt created during a particular simulation month.
    """

    principal: float
    interest_rate: float
    duration_months: int
    source: str


@dataclass(frozen=True)
class ScenarioEffect:
    """
    Changes produced by a scenario during one month.

    Recurring changes:
        income_delta
        expense_delta
        monthly_investment_override

    One-time changes:
        cash_delta
        asset_delta
        new_debt
    """

    income_delta: float = 0.0
    expense_delta: float = 0.0
    monthly_investment_override: float | None = None

    cash_delta: float = 0.0
    asset_delta: float = 0.0
    new_debt: NewDebtEffect | None = None


@dataclass(frozen=True)
class EffectiveMonthlyValues:
    """
    Monthly values after recurring scenario effects are applied.
    """

    income: float
    expenses: float
    monthly_investment: float


def _percentage_change(
    original_value: float,
    percentage: float,
) -> float:
    return original_value * percentage / 100


def _income_change_amount(
    scenario: IncomeChangeScenario,
    base_income: float,
) -> float:
    if scenario.amount is not None:
        return scenario.amount

    if scenario.percentage is not None:
        return _percentage_change(
            base_income,
            scenario.percentage,
        )

    raise ValueError(
        "Income change requires amount or percentage."
    )


def _expense_change_amount(
    scenario: ExpenseChangeScenario,
    base_expenses: float,
) -> float:
    if scenario.amount is not None:
        return scenario.amount

    if scenario.percentage is not None:
        return _percentage_change(
            base_expenses,
            scenario.percentage,
        )

    raise ValueError(
        "Expense change requires amount or percentage."
    )


def get_scenario_effect(
    scenario: Scenario,
    month: int,
    base_income: float,
    base_expenses: float,
) -> ScenarioEffect:
    """
    Calculate the effect of one scenario in one month.

    This function does not mutate the financial profile or
    perform investment growth, debt repayment, or cash-flow
    calculations.
    """

    if month < 1:
        raise ValueError("Month must be at least 1.")

    # --------------------------------------------------------
    # Loan
    # --------------------------------------------------------

    if isinstance(scenario, LoanScenario):
        if month != scenario.start_month:
            return ScenarioEffect()

        return ScenarioEffect(
            cash_delta=scenario.amount,
            new_debt=NewDebtEffect(
                principal=scenario.amount,
                interest_rate=scenario.interest_rate,
                duration_months=scenario.duration_months,
                source="loan",
            ),
        )

    # --------------------------------------------------------
    # Permanent income change
    # --------------------------------------------------------

    if isinstance(scenario, IncomeChangeScenario):
        if month < scenario.start_month:
            return ScenarioEffect()

        return ScenarioEffect(
            income_delta=_income_change_amount(
                scenario,
                base_income,
            )
        )

    # --------------------------------------------------------
    # Permanent expense change
    # --------------------------------------------------------

    if isinstance(scenario, ExpenseChangeScenario):
        if month < scenario.start_month:
            return ScenarioEffect()

        return ScenarioEffect(
            expense_delta=_expense_change_amount(
                scenario,
                base_expenses,
            )
        )

    # --------------------------------------------------------
    # Permanent investment-contribution change
    # --------------------------------------------------------

    if isinstance(scenario, InvestmentChangeScenario):
        if month < scenario.start_month:
            return ScenarioEffect()

        return ScenarioEffect(
            monthly_investment_override=(
                scenario.new_monthly_contribution
            )
        )

    # --------------------------------------------------------
    # Purchase
    # --------------------------------------------------------

    if isinstance(scenario, PurchaseScenario):
        if month != scenario.start_month:
            return ScenarioEffect()

        new_debt = None

        if scenario.financed_amount > 0:
            if (
                scenario.interest_rate is None
                or scenario.duration_months is None
            ):
                raise ValueError(
                    "Financed purchase is missing loan details."
                )

            new_debt = NewDebtEffect(
                principal=scenario.financed_amount,
                interest_rate=scenario.interest_rate,
                duration_months=scenario.duration_months,
                source="purchase",
            )

        return ScenarioEffect(
            cash_delta=-scenario.down_payment,
            asset_delta=scenario.price,
            new_debt=new_debt,
        )

    # --------------------------------------------------------
    # Temporary income loss
    # --------------------------------------------------------

    if isinstance(scenario, IncomeLossScenario):
        final_active_month = (
            scenario.start_month
            + scenario.duration_months
            - 1
        )

        is_active = (
            scenario.start_month
            <= month
            <= final_active_month
        )

        if not is_active:
            return ScenarioEffect()

        reduction = (
            base_income
            * scenario.income_reduction
            / 100
        )

        return ScenarioEffect(
            income_delta=-reduction
        )

    raise TypeError(
        f"Unsupported scenario type: {type(scenario).__name__}"
    )


def apply_recurring_effect(
    effect: ScenarioEffect,
    base_income: float,
    base_expenses: float,
    base_monthly_investment: float,
) -> EffectiveMonthlyValues:
    """
    Apply recurring effects and prevent income or expenses
    from becoming negative.
    """

    income = max(
        0.0,
        base_income + effect.income_delta,
    )

    expenses = max(
        0.0,
        base_expenses + effect.expense_delta,
    )

    if effect.monthly_investment_override is None:
        monthly_investment = base_monthly_investment
    else:
        monthly_investment = (
            effect.monthly_investment_override
        )

    return EffectiveMonthlyValues(
        income=income,
        expenses=expenses,
        monthly_investment=monthly_investment,
    )