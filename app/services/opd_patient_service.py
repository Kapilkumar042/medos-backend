from app.models.opd_patient import OpdPatient

from app.repositories.hospital_repository import (
    get_hospital_by_id
)

from app.utils.patient_number import (
    generate_uhid,
    generate_opd_no
)

from app.repositories.opd_patient_repository import (
    get_patient_by_id
)
from app.repositories.opd_patient_repository import create_patient

from app.repositories.opd_patient_repository import (get_patients_by_hospital)


def register_patient(
    db,
    payload,
    current_user
):

    hospital = get_hospital_by_id(
        db,
        current_user["hospital_id"]
    )

    uhid = generate_uhid(
        db,
        hospital
    )

    opd_no = generate_opd_no(
        db
    )

    patient = OpdPatient(

        hospital_id=current_user[
            "hospital_id"
        ],

        uhid=uhid,

        opd_no=opd_no,

        **payload.model_dump()
    )

    return create_patient(
        db,
        patient
    )


def get_patients(
    db,
    current_user
):

    return get_patients_by_hospital(
        db,
        current_user["hospital_id"]
    )


def get_patient(
    db,
    patient_id,
    current_user
):

    patient = get_patient_by_id(
        db,
        patient_id,
        current_user["hospital_id"]
    )

    if not patient:
        raise ValueError(
            "Patient not found"
        )

    return patient


def update_patient(
    db,
    patient_id,
    payload,
    current_user
):

    patient = get_patient_by_id(
        db,
        patient_id,
        current_user["hospital_id"]
    )

    if not patient:

        raise ValueError(
            "Patient not found"
        )

    patient.name = payload.name
    patient.mobile = payload.mobile
    patient.address = payload.address
    patient.gender = payload.gender
    patient.email = payload.email
    patient.symptoms = payload.symptoms
    patient.notes = payload.notes

    db.commit()

    db.refresh(patient)

    return patient
