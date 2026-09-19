from app.schemas.simulation import (
    SimulationRequest,
)
from app.simulation.engine import (
    compare_results,
    project_finances,
)
from app.simulation.monte_carlo import (
    compare_monte_carlo,
    run_monte_carlo,
)
from app.simulation.sensitivity import (
    run_sensitivity_analysis,
)


def build_warnings(
    *,
    request: SimulationRequest,
    deterministic_result: dict,
    monte_carlo_result: dict | None,
) -> list[str]:
    warnings: list[str] = []

    if (
        request.scenario is not None
        and request.scenario.start_month
        > request.projection_months
    ):
        warnings.append(
            "The scenario starts after the "
            "projection period and has no effect."
        )

    summary = deterministic_result[
        "final_summary"
    ]

    if summary["final_unfunded_deficit"] > 0:
        warnings.append(
            "Cash was depleted and some projected "
            "spending could not be funded."
        )

    if summary["final_remaining_debt"] > 0:
        warnings.append(
            "Debt remains at the end "
            "of the projection."
        )

    if summary["goal_reached"] is False:
        warnings.append(
            "The financial goal is not reached "
            "by the end of the deterministic "
            "projection."
        )

    if monte_carlo_result is not None:
        cash_depletion_probability = (
            monte_carlo_result[
                "probability_of_cash_depletion"
            ]
        )

        if cash_depletion_probability >= 25:
            warnings.append(
                "Monte Carlo analysis indicates a "
                f"{cash_depletion_probability}% "
                "probability of cash depletion."
            )

        goal_probability = (
            monte_carlo_result[
                "probability_of_reaching_goal"
            ]
        )

        if (
            goal_probability is not None
            and goal_probability < 50
        ):
            warnings.append(
                "Monte Carlo analysis indicates "
                f"only a {goal_probability}% "
                "probability of reaching the "
                "financial goal."
            )

    return warnings


def run_simulation_for_profile(
    *,
    profile,
    request: SimulationRequest,
) -> dict:
    """
    Run deterministic projections plus optional
    Monte Carlo and sensitivity analyses.
    """

    baseline = project_finances(
        profile=profile,
        assumptions=request.assumptions,
        projection_months=(
            request.projection_months
        ),
        scenario=None,
    )

    scenario_result = None
    deterministic_comparison = None

    if request.scenario is not None:
        scenario_result = project_finances(
            profile=profile,
            assumptions=request.assumptions,
            projection_months=(
                request.projection_months
            ),
            scenario=request.scenario,
        )

        deterministic_comparison = (
            compare_results(
                baseline=baseline,
                scenario_result=(
                    scenario_result
                ),
            )
        )

    monte_carlo_bundle = None
    monte_carlo_result_for_warnings = None

    if request.monte_carlo.enabled:
        baseline_monte_carlo = (
            run_monte_carlo(
                profile=profile,
                base_assumptions=(
                    request.assumptions
                ),
                projection_months=(
                    request.projection_months
                ),
                config=request.monte_carlo,
                scenario=None,
            )
        )

        scenario_monte_carlo = None
        monte_carlo_comparison = None

        if request.scenario is not None:
            # The same seed is used for a fair
            # baseline/scenario comparison.
            scenario_monte_carlo = (
                run_monte_carlo(
                    profile=profile,
                    base_assumptions=(
                        request.assumptions
                    ),
                    projection_months=(
                        request.projection_months
                    ),
                    config=request.monte_carlo,
                    scenario=request.scenario,
                )
            )

            monte_carlo_comparison = (
                compare_monte_carlo(
                    baseline_result=(
                        baseline_monte_carlo
                    ),
                    scenario_result=(
                        scenario_monte_carlo
                    ),
                )
            )

            monte_carlo_result_for_warnings = (
                scenario_monte_carlo
            )

        else:
            monte_carlo_result_for_warnings = (
                baseline_monte_carlo
            )

        monte_carlo_bundle = {
            "baseline": (
                baseline_monte_carlo
            ),
            "scenario": (
                scenario_monte_carlo
            ),
            "comparison": (
                monte_carlo_comparison
            ),
        }

    sensitivity_result = None

    if request.sensitivity.enabled:
        # If a scenario exists, sensitivity is
        # calculated for the scenario projection.
        # Otherwise it analyzes the baseline.
        sensitivity_result = (
            run_sensitivity_analysis(
                profile=profile,
                assumptions=(
                    request.assumptions
                ),
                projection_months=(
                    request.projection_months
                ),
                config=request.sensitivity,
                scenario=request.scenario,
            )
        )

    result_for_warnings = (
        scenario_result
        if scenario_result is not None
        else baseline
    )

    warnings = build_warnings(
        request=request,
        deterministic_result=(
            result_for_warnings
        ),
        monte_carlo_result=(
            monte_carlo_result_for_warnings
        ),
    )

    return {
        "baseline": baseline,
        "scenario": scenario_result,
        "comparison": (
            deterministic_comparison
        ),
        "monte_carlo": (
            monte_carlo_bundle
        ),
        "sensitivity": (
            sensitivity_result
        ),
        "warnings": warnings,
        "assumptions_used": (
            request.assumptions
        ),
    }