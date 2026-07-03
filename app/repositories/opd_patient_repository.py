from app.models.opd_patient import OpdPatient


def create_patient(
    db,
    patient
):

    db.add(patient)

    db.commit()

    db.refresh(patient)

    return patient


def get_patients_by_hospital(
    db,
    hospital_id
):

    return (
        db.query(OpdPatient)
        .filter(
            OpdPatient.hospital_id == hospital_id
        )
        .all()
    )


def get_patient_by_id(
    db,
    patient_id,
    hospital_id
):

    return (
        db.query(OpdPatient)
        .filter(
            OpdPatient.id == patient_id,
            OpdPatient.hospital_id == hospital_id
        )
        .first()
    )


# def get_patient_by_id(
#     db,
#     patient_id,
#     hospital_id
# ):
#     return (
#         db.query(OpdPatient)
#         .filter(
#             OpdPatient.id == patient_id,
#             OpdPatient.hospital_id == hospital_id
#         )
#         .first()
#     )
