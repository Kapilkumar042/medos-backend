from app.models.opd_visit import OpdVisit

from app.repositories.opd_visit_repository import (
    create_visit,
    get_visits_by_hospital
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
