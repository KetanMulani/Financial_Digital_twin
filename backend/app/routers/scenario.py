from fastapi import APIRouter, HTTPException, status

from app.schemas.scenario_parse import (
    ScenarioParseRequest,
    ScenarioParseResponse,
)
from app.services.llm_service import (
    LLMConfigurationError,
    LLMProviderError,
)
from app.services.scenario_service import (
    ScenarioParserError,
    parse_scenario,
)


router = APIRouter(
    prefix="/scenario",
    tags=["Scenario"],
)


@router.post(
    "/parse",
    response_model=ScenarioParseResponse,
    summary="Parse a natural-language financial scenario",
)
def parse_scenario_endpoint(
    request: ScenarioParseRequest,
) -> ScenarioParseResponse:
    try:
        result = parse_scenario(request.query)
    except LLMConfigurationError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    except LLMProviderError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc
    except ScenarioParserError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc

    return ScenarioParseResponse.model_validate(result)
