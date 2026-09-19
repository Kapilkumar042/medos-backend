from fastapi import APIRouter, Depends

from app.db.session import get_db
from app.auth.dependencies import get_current_user

from app.schemas.appointment import (
    CreateAppointmentRequest,
    UpdateAppointmentStatusRequest
)

from app.services.appointment_service import (
    create_appointment,
    get_appointments,
    accept_appointment,
    update_appointment_status
)

router = APIRouter(
    prefix="/appointments",
    tags=["Appointments"]
)


@router.post("")
def create_appointment_api(
    payload: CreateAppointmentRequest,
    db=Depends(get_db),
    current_user=Depends(get_current_user)
):
    return create_appointment(
        db,
        payload,
        current_user
    )


@router.get("")
def get_appointments_api(
    db=Depends(get_db),
    current_user=Depends(get_current_user)
):
    return get_appointments(
        db,
        current_user["hospital_id"]
    )


@router.put("/{appointment_id}/accept")
def accept_appointment_api(
    appointment_id: int,
    db=Depends(get_db),
    current_user=Depends(get_current_user)
):
    return accept_appointment(
        db,
        appointment_id,
        current_user["hospital_id"]
    )


@router.put("/{appointment_id}/status")
def update_status_api(
    appointment_id: int,
    payload: UpdateAppointmentStatusRequest,
    db=Depends(get_db),
    current_user=Depends(get_current_user)
):
    return update_appointment_status(
        db,
        appointment_id,
        payload.status,
        current_user["hospital_id"]
    )
