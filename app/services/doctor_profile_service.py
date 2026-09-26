import pandas as pd
from app.models.doctor_profile import DoctorProfile
from datetime import datetime

def generate_doctor_code(db, hospital_id):
    count = (
        db.query(DoctorProfile)
        .filter(
            DoctorProfile.hospital_id == hospital_id
        )
        .count()
    )

    return f"DOC{hospital_id}{count + 1:04d}"
def clean_value(value):
    return None if pd.isna(value) else value


def parse_time(value):
    if pd.isna(value) or value in ("", None):
        return None

    if hasattr(value, "time"):
        return value.time()

    try:
        return datetime.strptime(str(value), "%H:%M").time()
    except Exception:
        return None


def create_doctor(db, payload, current_user):
    if not payload.first_name or not payload.first_name.strip():
            raise ValueError("First name is required")
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
            DoctorProfile.hospital_id == hospital_id,
            # DoctorProfile.status != "Inactive",
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
    base_count = (
    db.query(DoctorProfile)
    .filter(DoctorProfile.hospital_id == hospital_id)
    .count()
    )

    for index, row in df.iterrows():
        first_name = row.get("first_name")
        # Skip row if first_name is empty
        if pd.isna(first_name) or str(first_name).strip() == "":
            continue

        doctor = DoctorProfile(
            hospital_id=hospital_id,
            doctor_code=f"DOC{hospital_id}{base_count + index + 1:04d}",

             first_name=str(first_name).strip(),
             last_name=(
                 str(row.get("last_name")).strip()
                 if pd.notna(row.get("last_name"))
                 else None
            ),
            gender=clean_value(row.get("gender")),
            email=clean_value(row.get("email")),
            phone=clean_value(row.get("phone")),
            alt_phone=clean_value(row.get("altPhone")),

            specialization=clean_value(row.get("specialization")),
            qualification=clean_value(row.get("qualification")),
            registration_no=clean_value(row.get("registration_no")),
            experience_years=clean_value(row.get("experience_years")),

            department=clean_value(row.get("department")),
            designation=clean_value(row.get("designation")),

            normal_fee=clean_value(row.get("normal_fee")),
            on_call_fee=clean_value(row.get("on_call_fee")),
            emergency_fee=clean_value(row.get("emergency_fee")),
            follow_up_fee=clean_value(row.get("follow_up_fee")),

            available_days=clean_value(row.get("available_days")),
            start_time=parse_time(row.get("start_time")),
            end_time=parse_time(row.get("end_time")),

            status=clean_value(row.get("status")) or "Active"
        )

        db.add(doctor)
        created.append(doctor)

    db.commit()

    return {
        "message": f"{len(created)} doctors imported successfully"
    }

def delete_doctor(db, doctor_id, hospital_id):
    doctor = (
        db.query(DoctorProfile)
        .filter(
            DoctorProfile.id == doctor_id,
            DoctorProfile.hospital_id == hospital_id,
        )
        .first()
    )

    if not doctor:
        return None

    doctor.status = "Inactive"
    db.commit()
    db.refresh(doctor)

    return doctor