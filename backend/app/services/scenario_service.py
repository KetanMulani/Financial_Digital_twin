from typing import Any

from pydantic import ValidationError

from app.schemas.scenario import scenario_adapter
from app.schemas.scenario_parse import LLMScenarioExtraction
from app.services.llm_service import LLMService, llm_service


class ScenarioParserError(ValueError):
    """The provider output could not be interpreted safely."""


SCENARIO_SYSTEM_PROMPT = """
You convert one natural-language financial what-if request into JSON.
You do not calculate projections, EMI, interest totals, or net worth.
Never invent a financial amount, interest rate, duration, or percentage.

Supported scenario types and allowed fields:

1. loan
   type, amount, interest_rate, duration_months, start_month

2. income_change
   type, exactly one of amount or percentage, start_month
   Use a negative value for a decrease.

3. expense_change
   type, exactly one of amount or percentage, start_month
   Use a negative value for a decrease.

4. investment_change
   type, new_monthly_contribution, start_month

5. purchase
   type, price, down_payment, financed_amount, start_month
   If financed_amount is greater than zero, also include interest_rate and
   duration_months. down_payment + financed_amount must equal price.

6. income_loss
   type, start_month, duration_months, income_reduction
   income_reduction is a percentage from greater than 0 through 100.

Timing conversions:
- immediately or now -> start_month 1
- next month -> start_month 2
- N years -> N multiplied by 12 months

Indian-number conversions:
- 1 lakh -> 100000
- 1 crore -> 10000000

If timing is not stated, use start_month 1 and add this exact assumption:
"No start time was provided; assumed month 1."

If any other required value is absent or ambiguous, omit it from scenario,
list its exact field name in missing_fields, and set requires_clarification
to true. Do not guess it.

Return only one JSON object with exactly these top-level fields:
{
  "scenario": {},
  "missing_fields": [],
  "assumptions": [],
  "requires_clarification": false
}
""".strip()


REQUIRED_FIELDS: dict[str, tuple[str, ...]] = {
    "loan": (
        "amount",
        "interest_rate",
        "duration_months",
        "start_month",
    ),
    "income_change": ("start_month",),
    "expense_change": ("start_month",),
    "investment_change": (
        "new_monthly_contribution",
        "start_month",
    ),
    "purchase": (
        "price",
        "down_payment",
        "financed_amount",
        "start_month",
    ),
    "income_loss": (
        "start_month",
        "duration_months",
        "income_reduction",
    ),
}


QUESTION_TEXT = {
    "type": "Which scenario do you want to model?",
    "amount": "What amount should be used?",
    "interest_rate": "What annual interest rate should be used?",
    "duration_months": "What is the duration in months?",
    "start_month": "In which simulation month should it begin?",
    "amount_or_percentage": (
        "Should the change use a fixed monthly amount or a percentage?"
    ),
    "new_monthly_contribution": (
        "What should the new monthly investment contribution be?"
    ),
    "price": "What is the total purchase price?",
    "down_payment": "What down payment will be made?",
    "financed_amount": "How much of the purchase will be financed?",
    "income_reduction": (
        "What percentage of income will be lost?"
    ),
    "scenario": "Please clarify the financial scenario details.",
}


def _unique_strings(values: list[Any]) -> list[str]:
    result: list[str] = []

    for value in values:
        if not isinstance(value, str):
            continue

        cleaned = value.strip()
        if cleaned and cleaned not in result:
            result.append(cleaned)

    return result


def _detect_missing_fields(
    scenario_data: dict[str, Any],
) -> list[str]:
    scenario_type = scenario_data.get("type")

    if scenario_type not in REQUIRED_FIELDS:
        return ["type"]

    missing = [
        field
        for field in REQUIRED_FIELDS[scenario_type]
        if field not in scenario_data or scenario_data[field] is None
    ]

    if scenario_type in {"income_change", "expense_change"}:
        has_amount = scenario_data.get("amount") is not None
        has_percentage = scenario_data.get("percentage") is not None

        if not has_amount and not has_percentage:
            missing.append("amount_or_percentage")

    if scenario_type == "purchase":
        financed_amount = scenario_data.get("financed_amount")

        if isinstance(financed_amount, (int, float)) and financed_amount > 0:
            for field in ("interest_rate", "duration_months"):
                if scenario_data.get(field) is None:
                    missing.append(field)

    return _unique_strings(missing)


def _questions_for(fields: list[str]) -> list[str]:
    return [
        QUESTION_TEXT.get(
            field,
            f"Please provide a valid value for {field}.",
        )
        for field in fields
    ]


def _fields_from_validation_error(
    error: ValidationError,
) -> list[str]:
    fields: list[str] = []

    for item in error.errors(include_url=False):
        location = item.get("loc", ())

        field = "scenario"
        if location:
            candidate = str(location[-1])
            if candidate not in REQUIRED_FIELDS:
                field = candidate

        if field not in fields:
            fields.append(field)

    return fields or ["scenario"]


def parse_scenario(
    query: str,
    *,
    client: LLMService | None = None,
) -> dict[str, Any]:
    """Convert natural language into a validated scenario or clarification."""

    cleaned_query = query.strip() if isinstance(query, str) else ""

    if not cleaned_query:
        raise ScenarioParserError("Scenario query cannot be empty.")

    provider = client or llm_service
    raw_result = provider.generate_json(
        system_prompt=SCENARIO_SYSTEM_PROMPT,
        user_prompt=cleaned_query,
    )

    try:
        extraction = LLMScenarioExtraction.model_validate(raw_result)
    except ValidationError as exc:
        raise ScenarioParserError(
            "The LLM returned an invalid scenario response structure."
        ) from exc

    scenario_data = dict(extraction.scenario)
    assumptions = _unique_strings(extraction.assumptions)

    if scenario_data.get("type") in REQUIRED_FIELDS:
        if scenario_data.get("start_month") is None:
            scenario_data["start_month"] = 1
            default_assumption = (
                "No start time was provided; assumed month 1."
            )
            if default_assumption not in assumptions:
                assumptions.append(default_assumption)

    detected_missing = _detect_missing_fields(scenario_data)
    reported_missing = _unique_strings(extraction.missing_fields)
    missing_fields = _unique_strings(
        detected_missing + reported_missing
    )

    if missing_fields:
        return {
            "query": cleaned_query,
            "scenario": scenario_data,
            "missing_fields": missing_fields,
            "clarification_questions": _questions_for(missing_fields),
            "assumptions": assumptions,
            "requires_clarification": True,
        }

    try:
        validated_scenario = scenario_adapter.validate_python(scenario_data)
    except ValidationError as exc:
        invalid_fields = _fields_from_validation_error(exc)

        return {
            "query": cleaned_query,
            "scenario": scenario_data,
            "missing_fields": invalid_fields,
            "clarification_questions": _questions_for(invalid_fields),
            "assumptions": assumptions,
            "requires_clarification": True,
        }

    if extraction.requires_clarification:
        return {
            "query": cleaned_query,
            "scenario": validated_scenario.model_dump(exclude_none=True),
            "missing_fields": ["scenario"],
            "clarification_questions": _questions_for(["scenario"]),
            "assumptions": assumptions,
            "requires_clarification": True,
        }

    return {
        "query": cleaned_query,
        "scenario": validated_scenario.model_dump(exclude_none=True),
        "missing_fields": [],
        "clarification_questions": [],
        "assumptions": assumptions,
        "requires_clarification": False,
    }
