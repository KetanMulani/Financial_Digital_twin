from dataclasses import dataclass
from typing import Protocol

from app.schemas.scenario import Scenario
from app.schemas.simulation import SimulationAssumptions
from app.simulation.scenario_effects import (
    ScenarioEffect,
    apply_recurring_effect,
    get_scenario_effect,
)


class ProfileLike(Protocol):
    """
    Fields required by the simulation engine.

    The SQLAlchemy TwinProfile model already provides
    these attributes.
    """

    monthly_income: float
    monthly_expenses: float
    cash_savings: float
    investments: float
    monthly_investment: float

    existing_debt: float
    debt_interest_rate: float
    monthly_debt_payment: float

    financial_goal: float | None


@dataclass
class DebtPosition:
    """
    One independently tracked debt.

    Existing debt and newly created scenario debts
    must not be merged because they may have different
    interest rates and monthly payments.
    """

    balance: float
    annual_interest_rate: float
    monthly_payment: float
    source: str


def calculate_emi(
    principal: float,
    annual_interest_rate: float,
    duration_months: int,
) -> float:
    """
    Calculate the fixed monthly EMI.
    """

    if principal <= 0:
        return 0.0

    if duration_months <= 0:
        raise ValueError(
            "Loan duration must be greater than zero."
        )

    monthly_rate = (
        annual_interest_rate / 100 / 12
    )

    if monthly_rate == 0:
        return principal / duration_months

    growth_factor = (
        1 + monthly_rate
    ) ** duration_months

    return (
        principal
        * monthly_rate
        * growth_factor
        / (growth_factor - 1)
    )


def annual_percentage_to_monthly_rate(
    annual_percentage: float,
) -> float:
    """
    Convert an effective annual percentage to an
    equivalent effective monthly rate.
    """

    return (
        1 + annual_percentage / 100
    ) ** (1 / 12) - 1


def process_debt_payment(
    debt: DebtPosition,
) -> tuple[float, float]:
    """
    Accrue one month of interest and apply one payment.

    Returns:
        payment made
        interest portion paid
    """

    if debt.balance <= 0:
        return 0.0, 0.0

    monthly_rate = (
        debt.annual_interest_rate / 100 / 12
    )

    interest_charged = (
        debt.balance * monthly_rate
    )

    total_amount_due = (
        debt.balance + interest_charged
    )

    payment = min(
        debt.monthly_payment,
        total_amount_due,
    )

    interest_paid = min(
        payment,
        interest_charged,
    )

    debt.balance = max(
        0.0,
        total_amount_due - payment,
    )

    return payment, interest_paid


def round_money(value: float) -> float:
    return round(float(value), 2)


def project_finances(
    *,
    profile: ProfileLike,
    assumptions: SimulationAssumptions,
    projection_months: int,
    scenario: Scenario | None = None,
) -> dict:
    """
    Run one deterministic financial projection.

    The same function is used for both the baseline
    and scenario projections.
    """

    if projection_months < 1:
        raise ValueError(
            "projection_months must be at least 1."
        )

    cash = float(profile.cash_savings)
    investments = float(profile.investments)

    scenario_assets = 0.0
    unfunded_deficit = 0.0

    debts: list[DebtPosition] = []

    # Track the user's existing debt independently.
    if profile.existing_debt > 0:
        debts.append(
            DebtPosition(
                balance=float(
                    profile.existing_debt
                ),
                annual_interest_rate=float(
                    profile.debt_interest_rate
                ),
                monthly_payment=float(
                    profile.monthly_debt_payment
                ),
                source="existing_debt",
            )
        )

    monthly_income_growth = (
        annual_percentage_to_monthly_rate(
            assumptions.annual_income_growth_rate
        )
    )

    monthly_expense_inflation = (
        annual_percentage_to_monthly_rate(
            assumptions
            .annual_expense_inflation_rate
        )
    )

    monthly_investment_return = (
        annual_percentage_to_monthly_rate(
            assumptions.annual_investment_return
        )
    )

    monthly_savings_interest = (
        annual_percentage_to_monthly_rate(
            assumptions
            .annual_savings_interest_rate
        )
    )

    timeline: list[dict] = []

    total_debt_payments = 0.0
    total_interest_paid = 0.0

    for month in range(
        1,
        projection_months + 1,
    ):
        # Apply normal income growth.
        base_income = (
            profile.monthly_income
            * (
                1 + monthly_income_growth
            ) ** (month - 1)
        )

        # Apply normal expense inflation.
        base_expenses = (
            profile.monthly_expenses
            * (
                1 + monthly_expense_inflation
            ) ** (month - 1)
        )

        # Calculate scenario effects for this month.
        if scenario is None:
            effect = ScenarioEffect()
        else:
            effect = get_scenario_effect(
                scenario=scenario,
                month=month,
                base_income=base_income,
                base_expenses=base_expenses,
            )

        effective_values = apply_recurring_effect(
            effect=effect,
            base_income=base_income,
            base_expenses=base_expenses,
            base_monthly_investment=(
                profile.monthly_investment
            ),
        )

        # Existing balances earn their monthly returns.
        cash *= (
            1 + monthly_savings_interest
        )

        investments *= (
            1 + monthly_investment_return
        )

        # Apply one-time scenario effects.
        cash += effect.cash_delta
        scenario_assets += effect.asset_delta

        # A large down payment must not make cash
        # silently negative.
        if cash < 0:
            unfunded_deficit += -cash
            cash = 0.0

        # Add a newly created loan or financed purchase.
        if effect.new_debt is not None:
            monthly_payment = calculate_emi(
                principal=(
                    effect.new_debt.principal
                ),
                annual_interest_rate=(
                    effect.new_debt.interest_rate
                ),
                duration_months=(
                    effect.new_debt.duration_months
                ),
            )

            debts.append(
                DebtPosition(
                    balance=(
                        effect.new_debt.principal
                    ),
                    annual_interest_rate=(
                        effect.new_debt.interest_rate
                    ),
                    monthly_payment=monthly_payment,
                    source=effect.new_debt.source,
                )
            )

        debt_payment = 0.0
        interest_paid = 0.0

        # Each debt has its own rate and payment.
        for debt in debts:
            payment, paid_interest = (
                process_debt_payment(debt)
            )

            debt_payment += payment
            interest_paid += paid_interest

        total_debt_payments += debt_payment
        total_interest_paid += interest_paid

        # The planned contribution enters investments.
        investment_contribution = (
            effective_values.monthly_investment
        )

        investments += investment_contribution

        monthly_surplus = (
            effective_values.income
            - effective_values.expenses
            - investment_contribution
            - debt_payment
        )

        if monthly_surplus >= 0:
            cash += monthly_surplus

        else:
            cash_required = -monthly_surplus

            cash_used = min(
                cash,
                cash_required,
            )

            cash -= cash_used

            unfunded_deficit += (
                cash_required - cash_used
            )

        remaining_debt = sum(
            debt.balance
            for debt in debts
        )

        # Unfunded deficit is treated as an additional
        # liability so that it does not falsely improve
        # the user's net worth.
        net_worth = (
            cash
            + investments
            + scenario_assets
            - remaining_debt
            - unfunded_deficit
        )

        timeline.append(
            {
                "month": month,
                "income": round_money(
                    effective_values.income
                ),
                "expenses": round_money(
                    effective_values.expenses
                ),
                "debt_payment": round_money(
                    debt_payment
                ),
                "investment_contribution": (
                    round_money(
                        investment_contribution
                    )
                ),
                "monthly_surplus": round_money(
                    monthly_surplus
                ),
                "cash_savings": round_money(
                    cash
                ),
                "investment_value": round_money(
                    investments
                ),
                "scenario_asset_value": (
                    round_money(
                        scenario_assets
                    )
                ),
                "remaining_debt": round_money(
                    remaining_debt
                ),
                "unfunded_deficit": round_money(
                    unfunded_deficit
                ),
                "net_worth": round_money(
                    net_worth
                ),
            }
        )

    final_month = timeline[-1]
    goal = profile.financial_goal

    if goal is None:
        goal_reached = None
    else:
        goal_reached = (
            final_month["net_worth"] >= goal
        )

    return {
        "timeline": timeline,
        "final_summary": {
            "final_cash_savings": (
                final_month["cash_savings"]
            ),
            "final_investment_value": (
                final_month["investment_value"]
            ),
            "final_scenario_asset_value": (
                final_month[
                    "scenario_asset_value"
                ]
            ),
            "final_remaining_debt": (
                final_month["remaining_debt"]
            ),
            "final_unfunded_deficit": (
                final_month[
                    "unfunded_deficit"
                ]
            ),
            "final_net_worth": (
                final_month["net_worth"]
            ),
            "total_debt_payments": (
                round_money(
                    total_debt_payments
                )
            ),
            "total_interest_paid": (
                round_money(
                    total_interest_paid
                )
            ),
            "goal": goal,
            "goal_reached": goal_reached,
        },
    }


def compare_results(
    baseline: dict,
    scenario_result: dict,
) -> dict:
    """
    Return scenario minus baseline for every
    important final value.
    """

    baseline_summary = (
        baseline["final_summary"]
    )

    scenario_summary = (
        scenario_result["final_summary"]
    )

    def difference(field: str) -> float:
        return round_money(
            scenario_summary[field]
            - baseline_summary[field]
        )

    return {
        "net_worth_difference": difference(
            "final_net_worth"
        ),
        "savings_difference": difference(
            "final_cash_savings"
        ),
        "investment_difference": difference(
            "final_investment_value"
        ),
        "asset_difference": difference(
            "final_scenario_asset_value"
        ),
        "debt_difference": difference(
            "final_remaining_debt"
        ),
        "unfunded_deficit_difference": (
            difference(
                "final_unfunded_deficit"
            )
        ),
    }