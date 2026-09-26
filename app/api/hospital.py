from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
)
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.db.session import get_db
from app.services.hospital_service import (
    get_hospital_profile,
    update_hospital_profile,
)

router = APIRouter(
    prefix="/hospital",
    tags=["Hospital Profile"],
)


@router.get("/profile")
def get_profile(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    profile = get_hospital_profile(
        db,
        current_user["hospital_id"],
    )

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Hospital not found",
        )

    return profile


@router.put("/profile")
def update_profile(
    hospital_name: str | None = Form(None),
    phone: str | None = Form(None),
    address: str | None = Form(None),
    modules: str | None = Form(None),
    logo: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    profile = update_hospital_profile(
        db=db,
        hospital_id=current_user["hospital_id"],
        hospital_name=hospital_name,
        phone=phone,
        address=address,
        modules=modules,
        logo=logo,
    )

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Hospital not found",
        )

    return profile