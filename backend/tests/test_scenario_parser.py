from typing import Any

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.config import Settings
from app.routers.scenario import router
from app.schemas.scenario_parse import ScenarioParseRequest
from app.services.llm_service import (
    LLMConfigurationError,
    LLMService,
)
from app.services.scenario_service import (
    ScenarioParserError,
    parse_scenario,
)


class FakeLLMService:
    def __init__(self, result: dict[str, Any]):
        self.result = result

    def generate_json(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
    ) -> dict[str, Any]:
        assert system_prompt
        assert user_prompt
        return self.result


def extraction(
    scenario: dict[str, Any],
    *,
    missing_fields: list[str] | None = None,
    assumptions: list[str] | None = None,
    requires_clarification: bool = False,
) -> dict[str, Any]:
    return {
        "scenario": scenario,
        "missing_fields": missing_fields or [],
        "assumptions": assumptions or [],
        "requires_clarification": requires_clarification,
    }


def test_complete_loan_is_validated():
    client = FakeLLMService(
        extraction(
            {
                "type": "loan",
                "amount": 1_000_000,
                "interest_rate": 9,
                "duration_months": 60,
                "start_month": 1,
            }
        )
    )

    result = parse_scenario(
        "Take a 10 lakh loan for five years at 9%",
        client=client,
    )

    assert result["requires_clarification"] is False
    assert result["missing_fields"] == []
    assert result["scenario"]["type"] == "loan"
    assert result["scenario"]["amount"] == 1_000_000
    assert result["scenario"]["duration_months"] == 60


def test_missing_timing_defaults_to_month_one():
    client = FakeLLMService(
        extraction(
            {
                "type": "investment_change",
                "new_monthly_contribution": 20_000,
            }
        )
    )

    result = parse_scenario(
        "Change my monthly investment to 20000",
        client=client,
    )

    assert result["scenario"]["start_month"] == 1
    assert (
        "No start time was provided; assumed month 1."
        in result["assumptions"]
    )


def test_incomplete_loan_requests_clarification():
    client = FakeLLMService(
        extraction(
            {
                "type": "loan",
                "amount": 1_000_000,
                "start_month": 1,
            },
            missing_fields=["interest_rate", "duration_months"],
            requires_clarification=True,
        )
    )

    result = parse_scenario(
        "What if I take a 10 lakh loan?",
        client=client,
    )

    assert result["requires_clarification"] is True
    assert result["missing_fields"] == [
        "interest_rate",
        "duration_months",
    ]
    assert len(result["clarification_questions"]) == 2


@pytest.mark.parametrize(
    "scenario",
    [
        {
            "type": "loan",
            "amount": 500_000,
            "interest_rate": 9,
            "duration_months": 60,
            "start_month": 1,
        },
        {
            "type": "income_change",
            "amount": 10_000,
            "start_month": 2,
        },
        {
            "type": "expense_change",
            "percentage": -10,
            "start_month": 2,
        },
        {
            "type": "investment_change",
            "new_monthly_contribution": 20_000,
            "start_month": 2,
        },
        {
            "type": "purchase",
            "price": 500_000,
            "down_payment": 100_000,
            "financed_amount": 400_000,
            "interest_rate": 9,
            "duration_months": 60,
            "start_month": 2,
        },
        {
            "type": "income_loss",
            "duration_months": 3,
            "income_reduction": 50,
            "start_month": 2,
        },
    ],
)
def test_all_six_scenario_types_are_supported(scenario):
    result = parse_scenario(
        "A financial scenario",
        client=FakeLLMService(extraction(scenario)),
    )

    assert result["requires_clarification"] is False
    assert result["scenario"]["type"] == scenario["type"]


def test_financed_purchase_requires_loan_details():
    client = FakeLLMService(
        extraction(
            {
                "type": "purchase",
                "price": 500_000,
                "down_payment": 100_000,
                "financed_amount": 400_000,
                "start_month": 1,
            }
        )
    )

    result = parse_scenario(
        "Buy something for five lakh with one lakh down",
        client=client,
    )

    assert result["requires_clarification"] is True
    assert "interest_rate" in result["missing_fields"]
    assert "duration_months" in result["missing_fields"]


def test_invalid_complete_scenario_becomes_clarification():
    client = FakeLLMService(
        extraction(
            {
                "type": "income_loss",
                "duration_months": 3,
                "income_reduction": 150,
                "start_month": 1,
            }
        )
    )

    result = parse_scenario(
        "I lose 150 percent of my income",
        client=client,
    )

    assert result["requires_clarification"] is True
    assert "income_reduction" in result["missing_fields"]


def test_unknown_scenario_type_requests_type():
    result = parse_scenario(
        "Do something unknown",
        client=FakeLLMService(
            extraction({"type": "unknown", "start_month": 1})
        ),
    )

    assert result["requires_clarification"] is True
    assert result["missing_fields"] == ["type"]


def test_empty_query_is_rejected():
    with pytest.raises(ScenarioParserError):
        parse_scenario(
            "   ",
            client=FakeLLMService(extraction({})),
        )


def test_invalid_llm_envelope_is_rejected():
    with pytest.raises(ScenarioParserError):
        parse_scenario(
            "Take a loan",
            client=FakeLLMService({"wrong": "shape"}),
        )


def test_json_decoder_accepts_code_fence():
    result = LLMService._decode_json(
        '```json\n{"scenario": {}}\n```'
    )

    assert result == {"scenario": {}}


def test_missing_provider_key_is_reported():
    service = LLMService(
        Settings(
            llm_provider="gemini",
            gemini_api_key=None,
            _env_file=None,
        )
    )

    with pytest.raises(LLMConfigurationError):
        service.generate_json(
            system_prompt="Return JSON",
            user_prompt="Test",
        )


def test_parse_request_rejects_whitespace_only_query():
    with pytest.raises(ValidationError):
        ScenarioParseRequest(query="   ")


def test_parse_endpoint(monkeypatch):
    import app.services.scenario_service as scenario_service

    monkeypatch.setattr(
        scenario_service,
        "llm_service",
        FakeLLMService(
            extraction(
                {
                    "type": "expense_change",
                    "percentage": -10,
                    "start_month": 2,
                }
            )
        ),
    )

    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)

    response = client.post(
        "/scenario/parse",
        json={"query": "Reduce expenses by 10% next month"},
    )

    assert response.status_code == 200
    assert response.json()["scenario"]["type"] == "expense_change"
    assert response.json()["requires_clarification"] is False
