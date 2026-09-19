from app.schemas.simulation import (
    SimulationRequest,
)
from app.simulation.engine import (
    compare_results,
    project_finances,
)


def build_warnings(
    *,
    request: SimulationRequest,
    result: dict,
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

    summary = result["final_summary"]

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
            "by the end of the projection."
        )

    return warnings


def run_simulation_for_profile(
    *,
    profile,
    request: SimulationRequest,
) -> dict:
    """
    Run the baseline first and then, when supplied,
    run the scenario using the same engine.
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
    comparison = None

    if request.scenario is not None:
        scenario_result = project_finances(
            profile=profile,
            assumptions=request.assumptions,
            projection_months=(
                request.projection_months
            ),
            scenario=request.scenario,
        )

        comparison = compare_results(
            baseline=baseline,
            scenario_result=scenario_result,
        )

    result_for_warnings = (
        scenario_result
        if scenario_result is not None
        else baseline
    )

    warnings = build_warnings(
        request=request,
        result=result_for_warnings,
    )

    return {
        "baseline": baseline,
        "scenario": scenario_result,
        "comparison": comparison,
        "warnings": warnings,
        "assumptions_used": request.assumptions,
    }