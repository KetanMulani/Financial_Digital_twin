from copy import deepcopy

from .engine import (
    FinancialProfile,
    LoanScenario,
    simulate_baseline,
    simulate_loan,
)


# ============================================================
# INTEREST RATE SENSITIVITY
# ============================================================

def sensitivity_interest_rate(
    profile: FinancialProfile,
    loan: LoanScenario,
    rates: list[float],
):
    """
    Test how different loan interest rates
    affect the final financial outcome.
    """

    results = []

    for rate in rates:

        scenario = deepcopy(loan)
        scenario.interest_rate = rate

        projection = simulate_loan(
            profile,
            scenario,
            months=60,
        )

        results.append({
            "parameter": "interest_rate",
            "value": rate,
            "final_net_worth": projection["final_net_worth"],
            "final_savings": projection["final_savings"],
            "final_investments": projection["final_investments"],
            "final_debt": projection["final_debt"],
            "emi": projection["scenario"]["emi"],
            "total_interest": projection["scenario"]["total_interest"],
        })

    return results


# ============================================================
# MONTHLY EXPENSE SENSITIVITY
# ============================================================

def sensitivity_monthly_expenses(
    profile: FinancialProfile,
    expense_values: list[float],
):
    """
    Test how different monthly expenses
    affect the final financial outcome.
    """

    results = []

    for expenses in expense_values:

        test_profile = deepcopy(profile)
        test_profile.monthly_expenses = expenses

        projection = simulate_baseline(
            test_profile,
            months=60,
        )

        results.append({
            "parameter": "monthly_expenses",
            "value": expenses,
            "final_net_worth": projection["final_net_worth"],
            "final_savings": projection["final_savings"],
            "final_investments": projection["final_investments"],
        })

    return results


# ============================================================
# MONTHLY INCOME SENSITIVITY
# ============================================================

def sensitivity_monthly_income(
    profile: FinancialProfile,
    income_values: list[float],
):
    """
    Test how different monthly incomes
    affect the final financial outcome.
    """

    results = []

    for income in income_values:

        test_profile = deepcopy(profile)
        test_profile.monthly_income = income

        projection = simulate_baseline(
            test_profile,
            months=60,
        )

        results.append({
            "parameter": "monthly_income",
            "value": income,
            "final_net_worth": projection["final_net_worth"],
            "final_savings": projection["final_savings"],
            "final_investments": projection["final_investments"],
        })

    return results


# ============================================================
# INVESTMENT RETURN SENSITIVITY
# ============================================================

def sensitivity_investment_return(
    profile: FinancialProfile,
    return_values: list[float],
):
    """
    Test how different annual investment returns
    affect the final financial outcome.
    """

    results = []

    for annual_return in return_values:

        projection = simulate_baseline(
            profile,
            months=60,
            annual_investment_return=annual_return,
        )

        results.append({
            "parameter": "investment_return",
            "value": annual_return,
            "final_net_worth": projection["final_net_worth"],
            "final_savings": projection["final_savings"],
            "final_investments": projection["final_investments"],
        })

    return results


# ============================================================
# INFLATION SENSITIVITY
# ============================================================

def sensitivity_inflation(
    profile: FinancialProfile,
    inflation_values: list[float],
):
    """
    Test how different annual inflation rates
    affect the final financial outcome.
    """

    results = []

    for inflation in inflation_values:

        projection = simulate_baseline(
            profile,
            months=60,
            annual_inflation=inflation,
        )

        results.append({
            "parameter": "inflation",
            "value": inflation,
            "final_net_worth": projection["final_net_worth"],
            "final_savings": projection["final_savings"],
            "final_investments": projection["final_investments"],
        })

    return results


# ============================================================
# MAIN TEST
# ============================================================

if __name__ == "__main__":

    profile = FinancialProfile(
        monthly_income=100000,
        monthly_expenses=45000,
        savings=500000,
        investments=300000,
        monthly_investment=20000,
        existing_debt=0,
    )

    loan = LoanScenario(
        amount=1000000,
        interest_rate=9,
        duration_months=60,
    )

    # --------------------------------------------------------
    # Interest Rate
    # --------------------------------------------------------

    print("\n--- Interest Rate Sensitivity ---")

    results = sensitivity_interest_rate(
        profile,
        loan,
        rates=[7, 8, 9, 10, 11, 12],
    )

    for result in results:
        print(
            f"{result['value']}% → "
            f"EMI ₹{result['emi']:,.2f} → "
            f"Net Worth ₹{result['final_net_worth']:,.2f}"
        )

    # --------------------------------------------------------
    # Expenses
    # --------------------------------------------------------

    print("\n--- Monthly Expense Sensitivity ---")

    results = sensitivity_monthly_expenses(
        profile,
        expense_values=[
            30000,
            35000,
            40000,
            45000,
            50000,
        ],
    )

    for result in results:
        print(
            f"₹{result['value']:,.0f}/month → "
            f"Net Worth ₹{result['final_net_worth']:,.2f}"
        )

    # --------------------------------------------------------
    # Income
    # --------------------------------------------------------

    print("\n--- Monthly Income Sensitivity ---")

    results = sensitivity_monthly_income(
        profile,
        income_values=[
            70000,
            80000,
            90000,
            100000,
            110000,
            120000,
        ],
    )

    for result in results:
        print(
            f"₹{result['value']:,.0f}/month → "
            f"Net Worth ₹{result['final_net_worth']:,.2f}"
        )

    # --------------------------------------------------------
    # Investment Return
    # --------------------------------------------------------

    print("\n--- Investment Return Sensitivity ---")

    results = sensitivity_investment_return(
        profile,
        return_values=[
            0.04,
            0.06,
            0.08,
            0.10,
            0.12,
            0.14,
        ],
    )

    for result in results:
        print(
            f"{result['value'] * 100:.0f}% → "
            f"Net Worth ₹{result['final_net_worth']:,.2f}"
        )

    # --------------------------------------------------------
    # Inflation
    # --------------------------------------------------------

    print("\n--- Inflation Sensitivity ---")

    results = sensitivity_inflation(
        profile,
        inflation_values=[
            0.02,
            0.03,
            0.04,
            0.05,
            0.06,
            0.07,
        ],
    )

    for result in results:
        print(
            f"{result['value'] * 100:.0f}% → "
            f"Net Worth ₹{result['final_net_worth']:,.2f}"
        )

    print("\nSensitivity analysis completed successfully.")