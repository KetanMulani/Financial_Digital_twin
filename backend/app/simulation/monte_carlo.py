import numpy as np

from app.schemas.scenario import Scenario
from app.schemas.simulation import (
    MonteCarloConfig,
    SimulationAssumptions,
)
from app.simulation.engine import (
    project_finances,
    round_money,
)


# These bounds prevent impossible annual rates.
# A return or growth rate cannot be below -100%.
MIN_RATE = -100.0
MAX_RATE = 100.0


def _percentile_summary(
    values: list[float],
) -> dict:
    """
    Convert a collection of simulation outputs into
    chart-ready summary statistics.
    """

    array = np.asarray(
        values,
        dtype=float,
    )

    return {
        "p10": round_money(
            np.percentile(array, 10)
        ),
        "p50": round_money(
            np.percentile(array, 50)
        ),
        "p90": round_money(
            np.percentile(array, 90)
        ),
        "mean": round_money(
            np.mean(array)
        ),
        "minimum": round_money(
            np.min(array)
        ),
        "maximum": round_money(
            np.max(array)
        ),
    }


def _sample_rates(
    *,
    rng: np.random.Generator,
    mean: float,
    standard_deviation: float,
    simulations: int,
) -> np.ndarray:
    """
    Sample rates and clip them to valid bounds.

    Rates are expressed in percentage points.
    """

    sampled_values = rng.normal(
        loc=mean,
        scale=standard_deviation,
        size=simulations,
    )

    return np.clip(
        sampled_values,
        MIN_RATE,
        MAX_RATE,
    )


def run_monte_carlo(
    *,
    profile,
    base_assumptions: SimulationAssumptions,
    projection_months: int,
    config: MonteCarloConfig,
    scenario: Scenario | None = None,
) -> dict:
    """
    Run repeated projections using uncertain financial
    assumptions.

    The supplied scenario remains deterministic, while
    investment return, income growth and expense
    inflation vary between simulation paths.
    """

    if projection_months < 1:
        raise ValueError(
            "projection_months must be at least 1."
        )

    if config.simulations < 1:
        raise ValueError(
            "simulations must be at least 1."
        )

    rng = np.random.default_rng(
        config.seed
    )

    investment_returns = _sample_rates(
        rng=rng,
        mean=(
            base_assumptions
            .annual_investment_return
        ),
        standard_deviation=(
            config.investment_return_std
        ),
        simulations=config.simulations,
    )

    income_growth_rates = _sample_rates(
        rng=rng,
        mean=(
            base_assumptions
            .annual_income_growth_rate
        ),
        standard_deviation=(
            config.income_growth_std
        ),
        simulations=config.simulations,
    )

    expense_inflation_rates = _sample_rates(
        rng=rng,
        mean=(
            base_assumptions
            .annual_expense_inflation_rate
        ),
        standard_deviation=(
            config.expense_inflation_std
        ),
        simulations=config.simulations,
    )

    final_net_worths: list[float] = []
    final_cash_savings: list[float] = []
    final_investment_values: list[float] = []

    goal_reached_count = 0
    cash_depletion_count = 0
    unfunded_deficit_count = 0

    for simulation_index in range(
        config.simulations
    ):
        sampled_assumptions = (
            SimulationAssumptions(
                annual_income_growth_rate=float(
                    income_growth_rates[
                        simulation_index
                    ]
                ),
                annual_expense_inflation_rate=float(
                    expense_inflation_rates[
                        simulation_index
                    ]
                ),
                annual_investment_return=float(
                    investment_returns[
                        simulation_index
                    ]
                ),
                # Savings interest remains deterministic.
                annual_savings_interest_rate=(
                    base_assumptions
                    .annual_savings_interest_rate
                ),
            )
        )

        projection = project_finances(
            profile=profile,
            assumptions=sampled_assumptions,
            projection_months=projection_months,
            scenario=scenario,
        )

        summary = projection[
            "final_summary"
        ]

        final_net_worths.append(
            summary["final_net_worth"]
        )

        final_cash_savings.append(
            summary["final_cash_savings"]
        )

        final_investment_values.append(
            summary["final_investment_value"]
        )

        if summary["goal_reached"] is True:
            goal_reached_count += 1

        cash_was_depleted = any(
            month["cash_savings"] <= 0
            for month in projection["timeline"]
        )

        if cash_was_depleted:
            cash_depletion_count += 1

        if (
            summary["final_unfunded_deficit"]
            > 0
        ):
            unfunded_deficit_count += 1

    probability_of_reaching_goal = None

    if profile.financial_goal is not None:
        probability_of_reaching_goal = (
            round_money(
                (
                    goal_reached_count
                    / config.simulations
                )
                * 100
            )
        )

    probability_of_cash_depletion = (
        round_money(
            (
                cash_depletion_count
                / config.simulations
            )
            * 100
        )
    )

    probability_of_unfunded_deficit = (
        round_money(
            (
                unfunded_deficit_count
                / config.simulations
            )
            * 100
        )
    )

    return {
        "simulations": config.simulations,
        "seed": config.seed,
        "final_net_worth": (
            _percentile_summary(
                final_net_worths
            )
        ),
        "final_cash_savings": (
            _percentile_summary(
                final_cash_savings
            )
        ),
        "final_investment_value": (
            _percentile_summary(
                final_investment_values
            )
        ),
        "probability_of_reaching_goal": (
            probability_of_reaching_goal
        ),
        "probability_of_cash_depletion": (
            probability_of_cash_depletion
        ),
        "probability_of_unfunded_deficit": (
            probability_of_unfunded_deficit
        ),
        "sampling_configuration": {
            "annual_investment_return": {
                "mean": (
                    base_assumptions
                    .annual_investment_return
                ),
                "standard_deviation": (
                    config.investment_return_std
                ),
                "minimum": MIN_RATE,
                "maximum": MAX_RATE,
            },
            "annual_income_growth_rate": {
                "mean": (
                    base_assumptions
                    .annual_income_growth_rate
                ),
                "standard_deviation": (
                    config.income_growth_std
                ),
                "minimum": MIN_RATE,
                "maximum": MAX_RATE,
            },
            "annual_expense_inflation_rate": {
                "mean": (
                    base_assumptions
                    .annual_expense_inflation_rate
                ),
                "standard_deviation": (
                    config.expense_inflation_std
                ),
                "minimum": MIN_RATE,
                "maximum": MAX_RATE,
            },
        },
    }


def compare_monte_carlo(
    baseline_result: dict,
    scenario_result: dict,
) -> dict:
    """
    Compare scenario percentiles and probabilities
    against the baseline Monte Carlo result.
    """

    baseline_net_worth = (
        baseline_result["final_net_worth"]
    )

    scenario_net_worth = (
        scenario_result["final_net_worth"]
    )

    baseline_goal_probability = (
        baseline_result[
            "probability_of_reaching_goal"
        ]
    )

    scenario_goal_probability = (
        scenario_result[
            "probability_of_reaching_goal"
        ]
    )

    if (
        baseline_goal_probability is None
        or scenario_goal_probability is None
    ):
        goal_probability_difference = None
    else:
        goal_probability_difference = (
            round_money(
                scenario_goal_probability
                - baseline_goal_probability
            )
        )

    return {
        "net_worth_p10_difference": (
            round_money(
                scenario_net_worth["p10"]
                - baseline_net_worth["p10"]
            )
        ),
        "net_worth_p50_difference": (
            round_money(
                scenario_net_worth["p50"]
                - baseline_net_worth["p50"]
            )
        ),
        "net_worth_p90_difference": (
            round_money(
                scenario_net_worth["p90"]
                - baseline_net_worth["p90"]
            )
        ),
        "goal_probability_difference": (
            goal_probability_difference
        ),
        "cash_depletion_probability_difference": (
            round_money(
                scenario_result[
                    "probability_of_cash_depletion"
                ]
                - baseline_result[
                    "probability_of_cash_depletion"
                ]
            )
        ),
        "unfunded_deficit_probability_difference": (
            round_money(
                scenario_result[
                    "probability_of_unfunded_deficit"
                ]
                - baseline_result[
                    "probability_of_unfunded_deficit"
                ]
            )
        ),
    }