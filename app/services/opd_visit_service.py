from app.models.opd_visit import OpdVisit


from app.repositories.opd_visit_repository import (
    create_visit,
    get_visits_by_hospital,
    get_visits_by_patient
)


def create_opd_visit(
    db,
    payload,
    current_user
):

    visit = OpdVisit(

        hospital_id=current_user[
            "hospital_id"
        ],

        patient_id=payload.patient_id,

        doctor_id=payload.doctor_id,

        department=payload.department,

        visit_date=payload.visit_date,

        symptoms=payload.symptoms,

        notes=payload.notes
    )

    return create_visit(
        db,
        visit
    )


def get_opd_visits(
    db,
    current_user
):

    return get_visits_by_hospital(
        db,
        current_user["hospital_id"]
    )

def get_opd_visits_for_patient(db, patient_id, current_user):
    return get_visits_by_patient(
        db,
        current_user["hospital_id"],
        patient_id
    )


def update_opd_visit(
    db,
    visit_id,
    payload,
    current_user
):
    hospital_id = current_user["hospital_id"]

    visit = (
        db.query(OpdVisit)
        .filter(
            OpdVisit.id == visit_id,
            OpdVisit.hospital_id == hospital_id
        )
        .first()
    )

    if not visit:
        return None

    data = payload.model_dump(
        exclude_unset=True
    )

    for key, value in data.items():
        setattr(visit, key, value)

    db.commit()
    db.refresh(visit)

    return visit
