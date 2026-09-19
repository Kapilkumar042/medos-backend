from app.models.appointment import Appointment
from app.models.opd_patient import OpdPatient
from app.repositories.hospital_repository import get_hospital_by_id
from app.utils.patient_number import generate_uhid, generate_opd_no
from app.repositories.opd_patient_repository import create_patient
from app.services.opd_queue_service import add_to_queue


def create_appointment(
    db,
    payload,
    current_user
):
    token = (
        db.query(Appointment)
        .filter(
            Appointment.hospital_id ==
            current_user["hospital_id"]
        )
        .count()
    ) + 1

    appointment = Appointment(
        hospital_id=current_user["hospital_id"],
        token=token,
        **payload.model_dump()
    )

    db.add(appointment)
    db.commit()
    db.refresh(appointment)

    return appointment


def get_appointments(
    db,
    hospital_id
):
    return (
        db.query(Appointment)
        .filter(
            Appointment.hospital_id ==
            hospital_id
        )
        .order_by(
            Appointment.id.desc()
        )
        .all()
    )


def accept_appointment(
    db,
    appointment_id,
    hospital_id
):
    appointment = (
        db.query(Appointment)
        .filter(
            Appointment.id == appointment_id,
            Appointment.hospital_id == hospital_id
        )
        .first()
    )
    print(
        "Creating OPD patient for appointment:",
        appointment.id
    )

    if not appointment:
        return None

    hospital = get_hospital_by_id(db, hospital_id)

    opd_patient = OpdPatient(
        hospital_id=hospital_id,
        uhid=generate_uhid(db, hospital),
        opd_no=generate_opd_no(db),
        name=appointment.patient_name,
        mobile=appointment.phone,
        gender=appointment.gender,
        blood_group=appointment.blood_group,
        age=appointment.age
    )

    created_patient = create_patient(db, opd_patient)

    queue = add_to_queue(
        db,
        created_patient.id,
        appointment.doctor_id,
        hospital_id
    )

    appointment.opd_patient_id = created_patient.id
    appointment.status = "Accepted"

    db.commit()
    db.refresh(appointment)

    return appointment


def update_appointment_status(
    db,
    appointment_id,
    status,
    hospital_id
):
    appointment = (
        db.query(Appointment)
        .filter(
            Appointment.id == appointment_id,
            Appointment.hospital_id == hospital_id
        )
        .first()
    )

    if not appointment:
        return None

    appointment.status = status

    db.commit()
    db.refresh(appointment)

    return appointment
