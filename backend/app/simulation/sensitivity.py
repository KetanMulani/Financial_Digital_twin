from types import SimpleNamespace

from app.schemas.scenario import Scenario
from app.schemas.simulation import (
    SensitivityConfig,
    SensitivityParameter,
    SimulationAssumptions,
)
from app.simulation.engine import (
    project_finances,
    round_money,
)


PROFILE_PARAMETERS = {
    "monthly_income",
    "monthly_expenses",
    "cash_savings",
    "investments",
    "monthly_investment",
    "existing_debt",
    "debt_interest_rate",
    "monthly_debt_payment",
}


ASSUMPTION_PARAMETERS = {
    "annual_income_growth_rate",
    "annual_expense_inflation_rate",
    "annual_investment_return",
    "annual_savings_interest_rate",
}


PROFILE_FIELDS = (
    "monthly_income",
    "monthly_expenses",
    "cash_savings",
    "investments",
    "monthly_investment",
    "existing_debt",
    "debt_interest_rate",
    "monthly_debt_payment",
    "financial_goal",
)


NON_NEGATIVE_PARAMETERS = PROFILE_PARAMETERS


# These match the limits used by the API schemas.
RATE_LIMITS = {
    "debt_interest_rate": (
        0.0,
        100.0,
    ),
    "annual_income_growth_rate": (
        -100.0,
        1000.0,
    ),
    "annual_expense_inflation_rate": (
        -100.0,
        1000.0,
    ),
    "annual_investment_return": (
        -100.0,
        1000.0,
    ),
    "annual_savings_interest_rate": (
        -100.0,
        1000.0,
    ),
}


def _copy_profile(
    profile,
) -> SimpleNamespace:
    """
    Copy only the profile fields required by the
    projection engine.

    This prevents sensitivity analysis from modifying
    the stored SQLAlchemy profile.
    """

    return SimpleNamespace(
        **{
            field: getattr(
                profile,
                field,
            )
            for field in PROFILE_FIELDS
        }
    )


def _bounded_value(
    *,
    parameter: SensitivityParameter,
    value: float,
) -> float:
    """
    Keep varied values within the same boundaries
    enforced by the API schemas.
    """

    if parameter in NON_NEGATIVE_PARAMETERS:
        value = max(
            0.0,
            value,
        )

    if parameter in RATE_LIMITS:
        minimum, maximum = (
            RATE_LIMITS[parameter]
        )

        value = min(
            maximum,
            max(
                minimum,
                value,
            ),
        )

    return float(value)


def _variation_values(
    *,
    parameter: SensitivityParameter,
    base_value: float,
    variation_percent: float,
) -> tuple[float, float]:
    """
    Calculate the low and high test values.
    """

    variation = (
        variation_percent / 100
    )

    first_value = _bounded_value(
        parameter=parameter,
        value=(
            base_value
            * (1 - variation)
        ),
    )

    second_value = _bounded_value(
        parameter=parameter,
        value=(
            base_value
            * (1 + variation)
        ),
    )

    return (
        min(
            first_value,
            second_value,
        ),
        max(
            first_value,
            second_value,
        ),
    )


def _run_with_parameter_value(
    *,
    profile,
    assumptions: SimulationAssumptions,
    projection_months: int,
    scenario: Scenario | None,
    parameter: SensitivityParameter,
    value: float,
) -> dict:
    """
    Run one projection with one modified input.
    """

    varied_profile = _copy_profile(
        profile
    )

    varied_assumptions = (
        assumptions.model_copy(
            deep=True
        )
    )

    if parameter in PROFILE_PARAMETERS:
        setattr(
            varied_profile,
            parameter,
            value,
        )

    elif parameter in ASSUMPTION_PARAMETERS:
        setattr(
            varied_assumptions,
            parameter,
            value,
        )

    else:
        raise ValueError(
            "Unsupported sensitivity parameter: "
            f"{parameter}"
        )

    return project_finances(
        profile=varied_profile,
        assumptions=varied_assumptions,
        projection_months=projection_months,
        scenario=scenario,
    )


def run_sensitivity_analysis(
    *,
    profile,
    assumptions: SimulationAssumptions,
    projection_months: int,
    config: SensitivityConfig,
    scenario: Scenario | None = None,
) -> dict:
    """
    Run one-at-a-time sensitivity analysis.

    Each selected input is decreased and increased by
    the configured percentage while all other inputs
    remain unchanged.

    Results are ranked by the range produced in final
    net worth.
    """

    if projection_months < 1:
        raise ValueError(
            "projection_months must be at least 1."
        )

    base_projection = project_finances(
        profile=profile,
        assumptions=assumptions,
        projection_months=projection_months,
        scenario=scenario,
    )

    base_final_net_worth = (
        base_projection[
            "final_summary"
        ][
            "final_net_worth"
        ]
    )

    results: list[dict] = []

    for parameter in config.parameters:
        if parameter in PROFILE_PARAMETERS:
            base_value = float(
                getattr(
                    profile,
                    parameter,
                )
            )

        elif parameter in ASSUMPTION_PARAMETERS:
            base_value = float(
                getattr(
                    assumptions,
                    parameter,
                )
            )

        else:
            raise ValueError(
                "Unsupported sensitivity parameter: "
                f"{parameter}"
            )

        low_value, high_value = (
            _variation_values(
                parameter=parameter,
                base_value=base_value,
                variation_percent=(
                    config.variation_percent
                ),
            )
        )

        low_projection = (
            _run_with_parameter_value(
                profile=profile,
                assumptions=assumptions,
                projection_months=(
                    projection_months
                ),
                scenario=scenario,
                parameter=parameter,
                value=low_value,
            )
        )

        high_projection = (
            _run_with_parameter_value(
                profile=profile,
                assumptions=assumptions,
                projection_months=(
                    projection_months
                ),
                scenario=scenario,
                parameter=parameter,
                value=high_value,
            )
        )

        low_final_net_worth = (
            low_projection[
                "final_summary"
            ][
                "final_net_worth"
            ]
        )

        high_final_net_worth = (
            high_projection[
                "final_summary"
            ][
                "final_net_worth"
            ]
        )

        results.append(
            {
                "parameter": parameter,
                "base_value": round_money(
                    base_value
                ),
                "low_value": round_money(
                    low_value
                ),
                "high_value": round_money(
                    high_value
                ),
                "base_final_net_worth": (
                    round_money(
                        base_final_net_worth
                    )
                ),
                "low_final_net_worth": (
                    round_money(
                        low_final_net_worth
                    )
                ),
                "high_final_net_worth": (
                    round_money(
                        high_final_net_worth
                    )
                ),
                "low_change": round_money(
                    low_final_net_worth
                    - base_final_net_worth
                ),
                "high_change": round_money(
                    high_final_net_worth
                    - base_final_net_worth
                ),
                "net_worth_range": (
                    round_money(
                        abs(
                            high_final_net_worth
                            - low_final_net_worth
                        )
                    )
                ),
                "normalized_impact": 0.0,
            }
        )

    maximum_range = max(
        (
            result[
                "net_worth_range"
            ]
            for result in results
        ),
        default=0.0,
    )

    for result in results:
        if maximum_range > 0:
            result[
                "normalized_impact"
            ] = round_money(
                result[
                    "net_worth_range"
                ]
                / maximum_range
                * 100
            )

    results.sort(
        key=lambda result: (
            result[
                "net_worth_range"
            ]
        ),
        reverse=True,
    )

    if results:
        most_sensitive_parameter = (
            results[0][
                "parameter"
            ]
        )
    else:
        most_sensitive_parameter = None

    return {
        "variation_percent": (
            config.variation_percent
        ),
        "base_final_net_worth": (
            round_money(
                base_final_net_worth
            )
        ),
        "ranking": results,
        "most_sensitive_parameter": (
            most_sensitive_parameter
        ),
    }