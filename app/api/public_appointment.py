from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.appointment import Appointment
from app.models.hospital import Hospital
from app.schemas.public_appointment import PublicAppointmentRequest
from app.models.doctor_profile import DoctorProfile

router = APIRouter(
    prefix="/public/appointments",
    tags=["Public Appointment"]
)


@router.post("")
def create_public_appointment(
    payload: PublicAppointmentRequest,
    db: Session = Depends(get_db)
):
    hospital = (
        db.query(Hospital)
        .filter(
            Hospital.id == payload.hospital_id,
            Hospital.is_active == True
        )
        .first()
    )

    if not hospital:
        raise HTTPException(
            status_code=404,
            detail="Hospital not found or inactive"
        )

    if payload.doctor_id is not None:
        doctor = (
            db.query(DoctorProfile)
            .filter(
                DoctorProfile.id == payload.doctor_id,
                DoctorProfile.hospital_id == payload.hospital_id,
                DoctorProfile.status == "Active"
            )
            .first()
        )

    if not doctor:
        raise HTTPException(
            status_code=400,
            detail="Selected doctor is not available"
        )

    token = (
        db.query(Appointment)
        .filter(
            Appointment.hospital_id == hospital.id
        )
        .count()
    ) + 1

    appointment_data = payload.model_dump()

    # hospital_id is used for ownership, not passed through blindly
    appointment_data.pop("hospital_id")

    appointment = Appointment(
        hospital_id=hospital.id,
        token=token,
        status="Scheduled",
        **appointment_data
    )

    db.add(appointment)
    db.commit()
    db.refresh(appointment)

    return {
        "message": "Appointment booked successfully",
        "appointment_id": appointment.id,
        "hospital_id": hospital.id,
        "hospital_name": hospital.hospital_name,
        "token": appointment.token,
        "status": appointment.status,
        "appointment_date": appointment.appointment_date,
        "appointment_time": appointment.appointment_time,
    }


@router.get("/hospitals/{hospital_id}")
def get_public_hospital(
    hospital_id: int,
    db: Session = Depends(get_db)
):
    hospital = (
        db.query(Hospital)
        .filter(Hospital.id == hospital_id)
        .first()
    )

    if not hospital:
        raise HTTPException(
            status_code=404,
            detail="Hospital not found"
        )

    return {
        "id": hospital.id,
        "hospital_name": hospital.hospital_name,
        "phone": hospital.phone,
    }


@router.get("/hospitals/{hospital_id}/doctors")
def get_public_doctors(
    hospital_id: int,
    db: Session = Depends(get_db)
):
    hospital = (
        db.query(Hospital)
        .filter(Hospital.id == hospital_id)
        .first()
    )

    if not hospital:
        raise HTTPException(
            status_code=404,
            detail="Hospital not found"
        )

    doctors = (
        db.query(DoctorProfile)
        .filter(
            DoctorProfile.hospital_id == hospital_id,
            DoctorProfile.status == "Active"
        )
        .order_by(
            DoctorProfile.first_name.asc()
        )
        .all()
    )

    return [
        {
            "id": doctor.id,
            "first_name": doctor.first_name,
            "last_name": doctor.last_name,
            "specialization": doctor.specialization,
            "department": doctor.department,
            "room_no": doctor.room_no,
        }
        for doctor in doctors
    ]
