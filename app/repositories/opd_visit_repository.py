from app.models.opd_visit import OpdVisit


def create_visit(
    db,
    visit
):
    db.add(visit)

    db.commit()

    db.refresh(visit)

    return visit


def get_visits_by_hospital(
    db,
    hospital_id
):
    return (
        db.query(OpdVisit)
        .filter(
            OpdVisit.hospital_id == hospital_id
        )
        .all()
    )
