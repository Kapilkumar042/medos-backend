from sqlalchemy.orm import Session

from app.models.hospital import Hospital


def get_hospital_by_email(
    db: Session,
    email: str
):
    return db.query(Hospital).filter(
        Hospital.email == email
    ).first()


def get_hospital_by_phone(
    db: Session,
    phone: str
):
    return (
        db.query(Hospital)
        .filter(Hospital.phone == phone)
        .first()
    )


def create_hospital(
    db: Session,
    hospital: Hospital
):
    db.add(hospital)
    db.commit()
    db.refresh(hospital)

    return hospital


def get_hospital_by_id(
    db,
    hospital_id
):

    return (
        db.query(Hospital)
        .filter(
            Hospital.id == hospital_id
        )
        .first()
    )
