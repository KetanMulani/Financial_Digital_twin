from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.twin_profile import TwinProfile
from app.schemas.simulation import (
    SimulationRequest,
    SimulationResponse,
)
from app.services.simulation_service import (
    run_simulation_for_profile,
)


router = APIRouter(
    prefix="/simulate",
    tags=["Simulation"],
)

DEMO_PROFILE_ID = 1


@router.post(
    "",
    response_model=SimulationResponse,
    summary=(
        "Compare the stored financial baseline "
        "with a what-if scenario"
    ),
)
def run_simulation(
    request: SimulationRequest,
    database: Session = Depends(get_db),
):
    profile = database.get(
        TwinProfile,
        DEMO_PROFILE_ID,
    )

    if profile is None:
        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail=(
                "Financial profile "
                "has not been created"
            ),
        )

    return run_simulation_for_profile(
        profile=profile,
        request=request,
    )