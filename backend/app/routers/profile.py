from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.twin_profile import TwinProfile
from app.schemas.twin_profile import (
    TwinProfileResponse,
    TwinProfileUpdate,
)

router = APIRouter(
    prefix="/profile",
    tags=["Financial Profile"],
)

DEMO_PROFILE_ID = 1


@router.get(
    "",
    response_model=TwinProfileResponse,
    summary="Get the financial profile",
)
def get_profile(
    database: Session = Depends(get_db),
) -> TwinProfile:
    profile = database.get(TwinProfile, DEMO_PROFILE_ID)

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Financial profile has not been created",
        )

    return profile


@router.put(
    "",
    response_model=TwinProfileResponse,
    summary="Create or update the financial profile",
)
def update_profile(
    profile_data: TwinProfileUpdate,
    database: Session = Depends(get_db),
) -> TwinProfile:
    profile = database.get(TwinProfile, DEMO_PROFILE_ID)

    validated_data = profile_data.model_dump()

    if profile is None:
        profile = TwinProfile(
            id=DEMO_PROFILE_ID,
            **validated_data,
        )
        database.add(profile)
    else:
        for field_name, value in validated_data.items():
            setattr(profile, field_name, value)

    database.commit()
    database.refresh(profile)

    return profile