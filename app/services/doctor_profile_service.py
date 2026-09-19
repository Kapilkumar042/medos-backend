import pandas as pd
from app.models.doctor_profile import DoctorProfile


def generate_doctor_code(db, hospital_id):
    count = (
        db.query(DoctorProfile)
        .filter(
            DoctorProfile.hospital_id == hospital_id
        )
        .count()
    )

    return f"DOC{hospital_id}{count + 1:04d}"


def create_doctor(db, payload, current_user):
    hospital_id = current_user["hospital_id"]

    doctor = DoctorProfile(
        hospital_id=hospital_id,
        doctor_code=generate_doctor_code(
            db,
            hospital_id
        ),
        **payload.model_dump()
    )

    db.add(doctor)
    db.commit()
    db.refresh(doctor)

    return doctor


def get_doctors(db, hospital_id):
    return (
        db.query(DoctorProfile)
        .filter(
            DoctorProfile.hospital_id == hospital_id
        )
        .all()
    )


def update_doctor(
    db,
    doctor_id,
    payload,
    hospital_id
):
    doctor = (
        db.query(DoctorProfile)
        .filter(
            DoctorProfile.id == doctor_id,
            DoctorProfile.hospital_id == hospital_id
        )
        .first()
    )

    if not doctor:
        return None

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(doctor, key, value)

    db.commit()
    db.refresh(doctor)

    return doctor


def import_doctors(
    db,
    file,
    current_user
):
    hospital_id = current_user["hospital_id"]

    df = pd.read_excel(file.file)

    # Validate required columns
    required_columns = [
        "first_name",
        "last_name",
        "email",
        "phone",
        "specialization"
    ]

    missing = [
        col
        for col in required_columns
        if col not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing columns: {', '.join(missing)}"
        )

    created = []

    for _, row in df.iterrows():

        doctor = DoctorProfile(
            hospital_id=hospital_id,
            doctor_code=generate_doctor_code(
                db,
                hospital_id
            ),

            first_name=row.get("first_name"),
            last_name=row.get("last_name"),
            gender=row.get("gender"),
            email=row.get("email"),
            phone=row.get("phone"),
            alt_phone=row.get("altPhone"),

            specialization=row.get("specialization"),
            qualification=row.get("qualification"),
            registration_no=row.get("registration_no"),
            experience_years=row.get("experience_years"),

            department=row.get("department"),
            designation=row.get("designation"),

            normal_fee=row.get("normal_fee"),
            on_call_fee=row.get("on_call_fee"),
            emergency_fee=row.get("emergency_fee"),
            follow_up_fee=row.get("follow_up_fee"),

            available_days=row.get("available_days"),
            start_time=row.get("start_time"),
            end_time=row.get("end_time"),

            status=row.get("status", "Active")
        )

        db.add(doctor)
        created.append(doctor)

    db.commit()

    return {
        "message": f"{len(created)} doctors imported successfully"
    }
