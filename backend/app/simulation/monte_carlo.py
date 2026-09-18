# backend/app/simulation/monte_carlo.py

import numpy as np
from typing import Callable

from .engine import (
    FinancialProfile,
    LoanScenario,
    simulate_baseline,
    simulate_loan,
)


# ============================================================
# MONTE CARLO CONFIGURATION
# ============================================================

DEFAULT_SIMULATIONS = 1000

# Expected annual investment return
DEFAULT_RETURN_MEAN = 0.10

# Standard deviation of annual investment return
DEFAULT_RETURN_STD = 0.05


# ============================================================
# MONTE CARLO - BASELINE
# ============================================================

def monte_carlo_baseline(
    profile: FinancialProfile,
    months: int = 60,
    simulations: int = DEFAULT_SIMULATIONS,
    return_mean: float = DEFAULT_RETURN_MEAN,
    return_std: float = DEFAULT_RETURN_STD,
    seed: int | None = 42,
) -> dict:
    """
    Run Monte Carlo simulations for the user's baseline
    financial situation.

    Each simulation uses a different randomly generated
    investment return.

    Returns:
        Summary statistics + all simulation results.
    """

    if simulations <= 0:
        raise ValueError("Number of simulations must be greater than 0")

    if months <= 0:
        raise ValueError("Number of months must be greater than 0")

    rng = np.random.default_rng(seed)

    # Generate random annual returns
    random_returns = rng.normal(
        loc=return_mean,
        scale=return_std,
        size=simulations,
    )

    final_net_worths = []
    final_savings = []
    final_investments = []

    simulation_results = []

    for i, annual_return in enumerate(random_returns):

        result = simulate_baseline(
            profile=profile,
            months=months,
            annual_investment_return=float(annual_return),
        )

        final_net_worth = result["final_net_worth"]
        savings = result["final_savings"]
        investments = result["final_investments"]

        final_net_worths.append(final_net_worth)
        final_savings.append(savings)
        final_investments.append(investments)

        simulation_results.append({
            "simulation": i + 1,
            "annual_return": round(
                float(annual_return) * 100,
                2
            ),
            "final_net_worth": round(
                final_net_worth,
                2
            ),
            "final_savings": round(
                savings,
                2
            ),
            "final_investments": round(
                investments,
                2
            ),
        })

    return {
        "type": "monte_carlo_baseline",

        "simulations": simulations,

        "months": months,

        "assumptions": {
            "return_mean": return_mean,
            "return_std": return_std,
        },

        "summary": {
            "p10": round(
                float(np.percentile(final_net_worths, 10)),
                2
            ),
            "p25": round(
                float(np.percentile(final_net_worths, 25)),
                2
            ),
            "p50": round(
                float(np.percentile(final_net_worths, 50)),
                2
            ),
            "p75": round(
                float(np.percentile(final_net_worths, 75)),
                2
            ),
            "p90": round(
                float(np.percentile(final_net_worths, 90)),
                2
            ),
            "mean": round(
                float(np.mean(final_net_worths)),
                2
            ),
            "minimum": round(
                float(np.min(final_net_worths)),
                2
            ),
            "maximum": round(
                float(np.max(final_net_worths)),
                2
            ),
        },

        "all_results": simulation_results,
    }


# ============================================================
# MONTE CARLO - LOAN SCENARIO
# ============================================================

def monte_carlo_loan(
    profile: FinancialProfile,
    scenario: LoanScenario,
    months: int = 60,
    simulations: int = DEFAULT_SIMULATIONS,
    return_mean: float = DEFAULT_RETURN_MEAN,
    return_std: float = DEFAULT_RETURN_STD,
    seed: int | None = 42,
) -> dict:
    """
    Run Monte Carlo simulations for a loan scenario.

    The loan itself remains deterministic.
    Investment returns vary between simulations.
    """

    if simulations <= 0:
        raise ValueError("Number of simulations must be greater than 0")

    if months <= 0:
        raise ValueError("Number of months must be greater than 0")

    rng = np.random.default_rng(seed)

    random_returns = rng.normal(
        loc=return_mean,
        scale=return_std,
        size=simulations,
    )

    final_net_worths = []
    final_savings = []
    final_investments = []

    simulation_results = []

    for i, annual_return in enumerate(random_returns):

        result = simulate_loan(
            profile=profile,
            scenario=scenario,
            months=months,
            annual_investment_return=float(annual_return),
        )

        final_net_worth = result["final_net_worth"]
        savings = result["final_savings"]
        investments = result["final_investments"]

        final_net_worths.append(final_net_worth)
        final_savings.append(savings)
        final_investments.append(investments)

        simulation_results.append({
            "simulation": i + 1,

            "annual_return": round(
                float(annual_return) * 100,
                2
            ),

            "final_net_worth": round(
                final_net_worth,
                2
            ),

            "final_savings": round(
                savings,
                2
            ),

            "final_investments": round(
                investments,
                2
            ),
        })

    return {
        "type": "monte_carlo_loan",

        "scenario": {
            "loan_amount": scenario.amount,
            "interest_rate": scenario.interest_rate,
            "duration_months": scenario.duration_months,
        },

        "simulations": simulations,

        "months": months,

        "assumptions": {
            "return_mean": return_mean,
            "return_std": return_std,
        },

        "summary": {
            "p10": round(
                float(np.percentile(final_net_worths, 10)),
                2
            ),

            "p25": round(
                float(np.percentile(final_net_worths, 25)),
                2
            ),

            "p50": round(
                float(np.percentile(final_net_worths, 50)),
                2
            ),

            "p75": round(
                float(np.percentile(final_net_worths, 75)),
                2
            ),

            "p90": round(
                float(np.percentile(final_net_worths, 90)),
                2
            ),

            "mean": round(
                float(np.mean(final_net_worths)),
                2
            ),

            "minimum": round(
                float(np.min(final_net_worths)),
                2
            ),

            "maximum": round(
                float(np.max(final_net_worths)),
                2
            ),
        },

        "all_results": simulation_results,
    }


# ============================================================
# COMPARE BASELINE VS SCENARIO
# ============================================================

def compare_monte_carlo(
    baseline_result: dict,
    scenario_result: dict,
) -> dict:
    """
    Compare Monte Carlo distributions between
    baseline and scenario.
    """

    baseline = baseline_result["summary"]
    scenario = scenario_result["summary"]

    return {
        "p10_difference": round(
            scenario["p10"] - baseline["p10"],
            2
        ),

        "p25_difference": round(
            scenario["p25"] - baseline["p25"],
            2
        ),

        "p50_difference": round(
            scenario["p50"] - baseline["p50"],
            2
        ),

        "p75_difference": round(
            scenario["p75"] - baseline["p75"],
            2
        ),

        "p90_difference": round(
            scenario["p90"] - baseline["p90"],
            2
        ),

        "mean_difference": round(
            scenario["mean"] - baseline["mean"],
            2
        ),
    }


# ============================================================
# SIMPLE TEST
# ============================================================

if __name__ == "__main__":

    # Example financial profile
    profile = FinancialProfile(
        monthly_income=100000,
        monthly_expenses=45000,
        savings=500000,
        investments=300000,
        monthly_investment=20000,
        existing_debt=0,
    )

    # Example ₹10 lakh loan
    loan = LoanScenario(
        amount=1000000,
        interest_rate=9,
        duration_months=60,
    )

    print("\n" + "=" * 60)
    print("MONTE CARLO FINANCIAL SIMULATION")
    print("=" * 60)

    # --------------------------------------------------------
    # Baseline
    # --------------------------------------------------------

    baseline = monte_carlo_baseline(
        profile=profile,
        months=60,
        simulations=1000,
    )

    print("\nBASELINE - 1000 SIMULATIONS")
    print("-" * 60)

    print(
        f"P10 Net Worth : ₹{baseline['summary']['p10']:,.2f}"
    )

    print(
        f"P25 Net Worth : ₹{baseline['summary']['p25']:,.2f}"
    )

    print(
        f"P50 Net Worth : ₹{baseline['summary']['p50']:,.2f}"
    )

    print(
        f"P75 Net Worth : ₹{baseline['summary']['p75']:,.2f}"
    )

    print(
        f"P90 Net Worth : ₹{baseline['summary']['p90']:,.2f}"
    )

    # --------------------------------------------------------
    # Loan scenario
    # --------------------------------------------------------

    loan_result = monte_carlo_loan(
        profile=profile,
        scenario=loan,
        months=60,
        simulations=1000,
    )

    print("\nLOAN SCENARIO - 1000 SIMULATIONS")
    print("-" * 60)

    print(
        f"P10 Net Worth : ₹{loan_result['summary']['p10']:,.2f}"
    )

    print(
        f"P25 Net Worth : ₹{loan_result['summary']['p25']:,.2f}"
    )

    print(
        f"P50 Net Worth : ₹{loan_result['summary']['p50']:,.2f}"
    )

    print(
        f"P75 Net Worth : ₹{loan_result['summary']['p75']:,.2f}"
    )

    print(
        f"P90 Net Worth : ₹{loan_result['summary']['p90']:,.2f}"
    )

    # --------------------------------------------------------
    # Comparison
    # --------------------------------------------------------

    comparison = compare_monte_carlo(
        baseline,
        loan_result,
    )

    print("\nCOMPARISON")
    print("-" * 60)

    print(
        f"P50 Difference : ₹{comparison['p50_difference']:,.2f}"
    )

    print(
        f"Mean Difference: ₹{comparison['mean_difference']:,.2f}"
    )

    print("\nMonte Carlo simulation completed successfully.")