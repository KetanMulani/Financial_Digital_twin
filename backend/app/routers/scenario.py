from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.services.scenario_service import parse_scenario


router = APIRouter(
    prefix="/scenario",
    tags=["Scenario"],
)


class ScenarioParseRequest(BaseModel):
    query: str


@router.post(
    "/parse",
    summary="Parse a natural-language financial scenario",
)
def parse_scenario_endpoint(request: ScenarioParseRequest):
    try:
        return parse_scenario(request.query)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Scenario parsing failed: {exc}",
        )