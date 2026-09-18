# backend/app/simulation/engine.py

from dataclasses import dataclass
from typing import Optional


# ============================================================
# DATA MODELS
# ============================================================

@dataclass
class FinancialProfile:
    monthly_income: float
    monthly_expenses: float
    savings: float
    investments: float
    monthly_investment: float
    existing_debt: float = 0.0


@dataclass
class LoanScenario:
    amount: float
    interest_rate: float
    duration_months: int


# ============================================================
# FINANCIAL CALCULATIONS
# ============================================================

def calculate_emi(
    principal: float,
    annual_interest_rate: float,
    duration_months: int
) -> float:
    """
    Calculate monthly EMI for a loan.
    """

    if principal <= 0:
        return 0.0

    if duration_months <= 0:
        raise ValueError("Loan duration must be greater than 0")

    monthly_rate = annual_interest_rate / 100 / 12

    # Zero-interest loan
    if monthly_rate == 0:
        return principal / duration_months

    emi = (
        principal
        * monthly_rate
        * (1 + monthly_rate) ** duration_months
        / (
            (1 + monthly_rate) ** duration_months - 1
        )
    )

    return emi


# ============================================================
# BASELINE SIMULATION
# ============================================================

def simulate_baseline(
    profile: FinancialProfile,
    months: int = 60,
    annual_investment_return: float = 0.10,
    annual_inflation: float = 0.05
) -> dict:
    """
    Simulate the user's financial situation without
    applying any new scenario.
    """

    savings = profile.savings
    investments = profile.investments
    debt = profile.existing_debt

    monthly_return = annual_investment_return / 12
    monthly_inflation = annual_inflation / 12

    results = []

    for month in range(1, months + 1):

        # Inflation-adjusted expenses
        expenses = (
            profile.monthly_expenses
            * (1 + monthly_inflation) ** (month - 1)
        )

        # Investment growth
        investment_growth = investments * monthly_return
        investments += investment_growth

        # Monthly investment contribution
        investments += profile.monthly_investment

        # Monthly cash flow
        cash_flow = (
            profile.monthly_income
            - expenses
            - profile.monthly_investment
        )

        savings += cash_flow

        # Net worth
        net_worth = savings + investments - debt

        results.append({
            "month": month,
            "income": round(profile.monthly_income, 2),
            "expenses": round(expenses, 2),
            "cash_flow": round(cash_flow, 2),
            "savings": round(savings, 2),
            "investments": round(investments, 2),
            "debt": round(debt, 2),
            "net_worth": round(net_worth, 2)
        })

    return {
        "type": "baseline",
        "months": months,
        "results": results,
        "final_savings": round(savings, 2),
        "final_investments": round(investments, 2),
        "final_debt": round(debt, 2),
        "final_net_worth": round(
            savings + investments - debt,
            2
        )
    }


# ============================================================
# LOAN SCENARIO
# ============================================================

def simulate_loan(
    profile: FinancialProfile,
    scenario: LoanScenario,
    months: int = 60,
    annual_investment_return: float = 0.10,
    annual_inflation: float = 0.05
) -> dict:
    """
    Simulate financial impact of taking a new loan.
    """

    savings = profile.savings
    investments = profile.investments

    # New loan added to existing debt
    debt = profile.existing_debt + scenario.amount

    emi = calculate_emi(
        scenario.amount,
        scenario.interest_rate,
        scenario.duration_months
    )

    monthly_loan_rate = (
        scenario.interest_rate / 100 / 12
    )

    monthly_return = annual_investment_return / 12
    monthly_inflation = annual_inflation / 12

    results = []

    total_interest = 0.0

    for month in range(1, months + 1):

        # -----------------------------------------
        # Expenses
        # -----------------------------------------

        expenses = (
            profile.monthly_expenses
            * (1 + monthly_inflation) ** (month - 1)
        )

        # -----------------------------------------
        # Investment growth
        # -----------------------------------------

        investment_growth = investments * monthly_return
        investments += investment_growth

        # -----------------------------------------
        # Loan calculation
        # -----------------------------------------

        loan_payment = 0.0
        interest_payment = 0.0
        principal_payment = 0.0

        if month <= scenario.duration_months and debt > 0:

            interest_payment = debt * monthly_loan_rate

            principal_payment = emi - interest_payment

            # Prevent overpayment in final month
            principal_payment = min(
                principal_payment,
                debt
            )

            loan_payment = (
                interest_payment + principal_payment
            )

            debt -= principal_payment

            total_interest += interest_payment

        # -----------------------------------------
        # Investment contribution
        # -----------------------------------------

        investments += profile.monthly_investment

        # -----------------------------------------
        # Cash flow
        # -----------------------------------------

        cash_flow = (
            profile.monthly_income
            - expenses
            - loan_payment
            - profile.monthly_investment
        )

        savings += cash_flow

        # -----------------------------------------
        # Net worth
        # -----------------------------------------

        net_worth = (
            savings
            + investments
            - debt
        )

        results.append({
            "month": month,
            "income": round(profile.monthly_income, 2),
            "expenses": round(expenses, 2),
            "loan_payment": round(loan_payment, 2),
            "interest_payment": round(
                interest_payment, 2
            ),
            "principal_payment": round(
                principal_payment, 2
            ),
            "cash_flow": round(cash_flow, 2),
            "savings": round(savings, 2),
            "investments": round(investments, 2),
            "debt": round(max(debt, 0), 2),
            "net_worth": round(net_worth, 2)
        })

    return {
        "type": "loan",

        "scenario": {
            "loan_amount": scenario.amount,
            "interest_rate": scenario.interest_rate,
            "duration_months": scenario.duration_months,
            "emi": round(emi, 2),
            "total_interest": round(total_interest, 2)
        },

        "months": months,

        "results": results,

        "final_savings": round(savings, 2),
        "final_investments": round(investments, 2),
        "final_debt": round(max(debt, 0), 2),
        "final_net_worth": round(
            savings + investments - max(debt, 0),
            2
        )
    }


# ============================================================
# COMPARISON
# ============================================================

def compare_results(
    baseline: dict,
    scenario: dict
) -> dict:
    """
    Compare baseline and scenario results.
    """

    return {
        "savings_difference": round(
            scenario["final_savings"]
            - baseline["final_savings"],
            2
        ),

        "investment_difference": round(
            scenario["final_investments"]
            - baseline["final_investments"],
            2
        ),

        "debt_difference": round(
            scenario["final_debt"]
            - baseline["final_debt"],
            2
        ),

        "net_worth_difference": round(
            scenario["final_net_worth"]
            - baseline["final_net_worth"],
            2
        )
    }


# ============================================================
# MAIN TEST
# ============================================================

if __name__ == "__main__":

    # Example user financial profile
    profile = FinancialProfile(
        monthly_income=100000,
        monthly_expenses=45000,
        savings=500000,
        investments=300000,
        monthly_investment=20000,
        existing_debt=0
    )

    # Example scenario:
    # ₹10 lakh loan, 9% interest, 5 years
    loan = LoanScenario(
        amount=1000000,
        interest_rate=9,
        duration_months=60
    )

    print("\n" + "=" * 60)
    print("FINANCIAL DIGITAL TWIN - SIMULATION ENGINE")
    print("=" * 60)

    # -----------------------------------------
    # Baseline
    # -----------------------------------------

    baseline = simulate_baseline(
        profile,
        months=60
    )

    # -----------------------------------------
    # Loan scenario
    # -----------------------------------------

    scenario = simulate_loan(
        profile,
        loan,
        months=60
    )

    # -----------------------------------------
    # Comparison
    # -----------------------------------------

    comparison = compare_results(
        baseline,
        scenario
    )

    # -----------------------------------------
    # Display
    # -----------------------------------------

    print("\nBASELINE")
    print("-" * 60)

    print(
        f"Final Savings     : ₹{baseline['final_savings']:,.2f}"
    )

    print(
        f"Final Investments : ₹{baseline['final_investments']:,.2f}"
    )

    print(
        f"Final Debt        : ₹{baseline['final_debt']:,.2f}"
    )

    print(
        f"Final Net Worth   : ₹{baseline['final_net_worth']:,.2f}"
    )

    print("\nLOAN SCENARIO")
    print("-" * 60)

    print(
        f"Loan Amount       : ₹{loan.amount:,.2f}"
    )

    print(
        f"Interest Rate     : {loan.interest_rate}%"
    )

    print(
        f"Duration          : {loan.duration_months} months"
    )

    print(
        f"Monthly EMI       : ₹{scenario['scenario']['emi']:,.2f}"
    )

    print(
        f"Total Interest    : ₹{scenario['scenario']['total_interest']:,.2f}"
    )

    print(
        f"Final Savings     : ₹{scenario['final_savings']:,.2f}"
    )

    print(
        f"Final Investments : ₹{scenario['final_investments']:,.2f}"
    )

    print(
        f"Final Debt        : ₹{scenario['final_debt']:,.2f}"
    )

    print(
        f"Final Net Worth   : ₹{scenario['final_net_worth']:,.2f}"
    )

    print("\nDIFFERENCE")
    print("-" * 60)

    print(
        f"Savings           : ₹{comparison['savings_difference']:,.2f}"
    )

    print(
        f"Investments       : ₹{comparison['investment_difference']:,.2f}"
    )

    print(
        f"Debt              : ₹{comparison['debt_difference']:,.2f}"
    )

    print(
        f"Net Worth         : ₹{comparison['net_worth_difference']:,.2f}"
    )

    print("\nMONTH 1")
    print("-" * 60)

    print(scenario["results"][0])

    print("\nMONTH 60")
    print("-" * 60)

    print(scenario["results"][-1])

    print("\nSimulation completed successfully.")