from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.auth.dependencies import (
    get_current_user
)
from fastapi import Depends

from app.schemas.hospital import (
    HospitalRegister,
    HospitalLogin
)

from app.services.hospital_service import (
    register_hospital,
    login_hospital
)

from app.db.dependencies import (
    get_db
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post("/register")
def register(
    payload: HospitalRegister,
    db: Session = Depends(get_db)
):

    try:

        hospital = register_hospital(
            db,
            payload
        )

        return {
            "message":
            "Hospital Registered Successfully",

            "hospital_id":
            hospital.id
        }

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.post("/login")
def login(
    payload: HospitalLogin,
    db: Session = Depends(get_db)
):

    try:

        return login_hospital(
            db,
            payload
        )

    except ValueError as e:

        raise HTTPException(
            status_code=401,
            detail=str(e)
        )

@router.get("/me")
def get_me(
    current_user=Depends(
        get_current_user
    )
):
    return current_user    