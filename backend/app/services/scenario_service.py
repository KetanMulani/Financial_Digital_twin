from typing import Any

from pydantic import ValidationError

from app.schemas.scenario import scenario_adapter
from app.services.llm_service import llm_service


SCENARIO_SYSTEM_PROMPT = """
You are a financial scenario parser for a Financial Digital Twin.

Your job is ONLY to convert the user's natural-language
financial "what-if" request into structured JSON.

Do NOT:
- calculate EMI
- calculate loan interest
- calculate net worth
- perform financial projections
- provide financial advice
- invent missing financial values
- invent loan interest rates
- invent loan durations
- invent purchase prices
- invent income values

The simulation engine performs all financial calculations.

Supported scenario types:

1. loan
2. income_change
3. expense_change
4. investment_change
5. purchase
6. income_loss


LOAN
Required fields:
- type
- amount
- interest_rate
- duration_months
- start_month

Example:
"What if I take a 10 lakh loan for 5 years at 9 percent?"

Return:

{
    "scenario": {
        "type": "loan",
        "amount": 1000000,
        "interest_rate": 9,
        "duration_months": 60,
        "start_month": 1
    },
    "missing_fields": [],
    "assumptions": [],
    "requires_clarification": false
}


INCOME_CHANGE
Required:
- type
- start_month
- exactly one of amount or percentage

Example:
"What if my salary increases by 20000 starting next month?"

Return:

{
    "scenario": {
        "type": "income_change",
        "amount": 20000,
        "start_month": 2
    },
    "missing_fields": [],
    "assumptions": [],
    "requires_clarification": false
}


EXPENSE_CHANGE
Required:
- type
- start_month
- exactly one of amount or percentage


INVESTMENT_CHANGE
Required:
- type
- new_monthly_contribution
- start_month


PURCHASE
Required:
- type
- price
- down_payment
- financed_amount
- start_month

The following must be true:

down_payment + financed_amount = price


INCOME_LOSS
Required:
- type
- start_month
- duration_months
- income_reduction

income_reduction is a percentage.


IMPORTANT:

If a required value is missing, DO NOT invent it.

Return the available information and list the missing
fields in "missing_fields".

Set "requires_clarification" to true.

For example:

User:
"What if I take a 10 lakh loan?"

Return:

{
    "scenario": {
        "type": "loan",
        "amount": 1000000,
        "start_month": 1
    },
    "missing_fields": [
        "interest_rate",
        "duration_months"
    ],
    "assumptions": [],
    "requires_clarification": true
}


If the user clearly means the scenario starts immediately,
use:

"start_month": 1


For "next month", use:

"start_month": 2


Convert common time expressions:

1 year = 12 months
2 years = 24 months
3 years = 36 months
5 years = 60 months


Convert Indian currency expressions:

10 lakh = 1000000
5 lakh = 500000
1 crore = 10000000


Do not include fields that do not belong to the
specific scenario type.

Return ONLY valid JSON.

The top-level response must have:

{
    "scenario": {},
    "missing_fields": [],
    "assumptions": [],
    "requires_clarification": false
}
"""


def parse_scenario(query: str) -> dict[str, Any]:
    """
    Convert natural-language financial input into
    a validated structured scenario.
    """

    if not query or not query.strip():
        raise ValueError(
            "Scenario query cannot be empty."
        )

    result = llm_service.generate_json(
        system_prompt=SCENARIO_SYSTEM_PROMPT,
        user_prompt=query.strip(),
    )

    if not isinstance(result, dict):
        raise ValueError(
            "LLM response must be a JSON object."
        )

    scenario_data = result.get("scenario")

    if scenario_data is None:
        raise ValueError(
            "LLM response does not contain a scenario."
        )

    missing_fields = result.get(
        "missing_fields",
        []
    )

    assumptions = result.get(
        "assumptions",
        []
    )

    requires_clarification = result.get(
        "requires_clarification",
        False
    )

    # Missing information means we should not
    # attempt Pydantic validation yet.
    if missing_fields:
        return {
            "scenario": scenario_data,
            "missing_fields": missing_fields,
            "assumptions": assumptions,
            "requires_clarification": True,
        }

    # Validate the scenario against your exact
    # discriminated Scenario union.
    try:
        validated_scenario = scenario_adapter.validate_python(
            scenario_data
        )

    except ValidationError as exc:
        raise ValueError(
            f"Invalid scenario returned by LLM: {exc}"
        ) from exc

    return {
        "scenario": validated_scenario.model_dump(),
        "missing_fields": [],
        "assumptions": assumptions,
        "requires_clarification": requires_clarification,
    }