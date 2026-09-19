from app.models.opd_patient import OpdPatient

from app.repositories.hospital_repository import (
    get_hospital_by_id
)
from app.services.opd_bill_service import create_opd_bill

from app.schemas.opd_bill import (
    CreateBillRequest,
    BillItemRequest
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

from app.services.opd_queue_service import add_to_queue


# def register_patient(
#     db,
#     payload,
#     current_user
# ):

#     hospital = get_hospital_by_id(
#         db,
#         current_user["hospital_id"]
#     )

#     uhid = generate_uhid(
#         db,
#         hospital
#     )

#     opd_no = generate_opd_no(
#         db
#     )

#     patient = OpdPatient(

#         hospital_id=current_user[
#             "hospital_id"
#         ],

#         uhid=uhid,

#         opd_no=opd_no,

#         **payload.model_dump()
#     )

#     return create_patient(
#         db,
#         patient
#     )

def register_patient(
    db,
    payload,
    current_user
):
    hospital_id = current_user["hospital_id"]

    hospital = get_hospital_by_id(
        db,
        hospital_id
    )

    uhid = generate_uhid(
        db,
        hospital
    )

    opd_no = generate_opd_no(
        db
    )

    patient_data = payload.model_dump()

    # doctor_id belongs to the queue, not the patient table
    doctor_id = patient_data.pop(
        "doctor_id",
        None
    )

    patient = OpdPatient(
        hospital_id=hospital_id,
        uhid=uhid,
        opd_no=opd_no,
        **patient_data
    )

    created_patient = create_patient(
        db,
        patient
    )

    add_to_queue(
        db,
        patient_id=created_patient.id,
        doctor_id=doctor_id,
        hospital_id=hospital_id
    )

    return created_patient


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

    data = payload.model_dump(exclude_unset=True)

    for key, value in data.items():
        setattr(patient, key, value)

    db.commit()
    db.refresh(patient)

    return patient
