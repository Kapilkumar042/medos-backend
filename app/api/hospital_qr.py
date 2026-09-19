from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.db.session import get_db

from app.auth.dependencies import (
    get_current_user
)

from app.services.hospital_service import (
    create_hospital_qr
)

router = APIRouter(
    prefix="/api/hospital",
    tags=["Hospital QR"]
)


@router.get("/generate-qr")
def generate_qr(
    db: Session = Depends(get_db),
    current_user=Depends(
        get_current_user
    )
):
    print("CURRENT USER:", current_user)
    print("CURRENT HOSPITAL ID:", current_user.get("hospital_id"))
    qr = create_hospital_qr(
        db,
        current_user["hospital_id"]
    )

    if not qr:
        raise HTTPException(
            status_code=404,
            detail="Hospital not found"
        )

    return qr
