from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.doctor_profile_service import import_doctors

from app.auth.dependencies import get_current_user

from app.schemas.doctor_profile import (
    CreateDoctorProfileRequest,
    UpdateDoctorProfileRequest
)

from app.services.doctor_profile_service import (
    create_doctor,
    get_doctors,
    update_doctor,
    delete_doctor,
)

router = APIRouter(
    prefix="/doctors",
    tags=["Doctors"]
)


@router.post("")
def create_doctor_api(
    payload: CreateDoctorProfileRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return create_doctor(
        db,
        payload,
        current_user
    )


@router.get("")
def get_doctors_api(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return get_doctors(
        db,
        current_user["hospital_id"]
    )


@router.put("/{doctor_id}")
def update_doctor_api(
    doctor_id: int,
    payload: UpdateDoctorProfileRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return update_doctor(
        db,
        doctor_id,
        payload,
        current_user["hospital_id"]
    )


@router.post("/import")
def import_doctors_api(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return import_doctors(
        db,
        file,
        current_user
    )


@router.delete("/{doctor_id}")
def delete_doctor_api(
    doctor_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    doctor = delete_doctor(
        db,
        doctor_id,
        current_user["hospital_id"],
    )

    if not doctor:
        raise HTTPException(
            status_code=404,
            detail="Doctor not found",
        )

    return {
        "message": "Doctor deactivated successfully",
        "doctor_id": doctor.id,
    }