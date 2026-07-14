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
