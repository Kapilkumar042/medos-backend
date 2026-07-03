from app.models.doctor_profile import (
    DoctorProfile
)


def create_doctor_profile(
    db,
    doctor
):

    db.add(doctor)

    db.commit()

    db.refresh(doctor)

    return doctor


def get_doctors_by_hospital(
    db,
    hospital_id
):

    return (
        db.query(DoctorProfile)
        .filter(
            DoctorProfile.hospital_id
            == hospital_id
        )
        .all()
    )


def get_doctor_by_id(
    db,
    doctor_id,
    hospital_id
):

    return (
        db.query(
            DoctorProfile
        )
        .filter(
            DoctorProfile.id
            == doctor_id,

            DoctorProfile.hospital_id
            == hospital_id
        )
        .first()
    )


def get_doctor_by_user_id(
    db,
    user_id
):

    return (
        db.query(DoctorProfile)
        .filter(
            DoctorProfile.user_id == user_id
        )
        .first()
    )
