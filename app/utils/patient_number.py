from datetime import date

from app.models.opd_patient import OpdPatient
from app.models.hospital import Hospital


def generate_hospital_code(
    hospital_name,
    hospital_id
):

    prefix = (
        hospital_name
        .replace(" ", "")
        .upper()[:2]
    )

    return f"{prefix}{hospital_id:02d}"


def generate_uhid(
    db,
    hospital
):

    count = (
        db.query(OpdPatient)
        .filter(
            OpdPatient.hospital_id == hospital.id
        )
        .count()
    )

    code = generate_hospital_code(
        hospital.hospital_name,
        hospital.id
    )

    return f"{code}{count + 1:06d}"


def generate_opd_no(
    db
):

    today = date.today()

    count = (
        db.query(OpdPatient)
        .filter(
            OpdPatient.created_at >= today
        )
        .count()
    )

    return (
        f"OPD"
        f"{today.strftime('%Y%m%d')}"
        f"{count + 1:04d}"
    )
