from app.models.user import User

from app.models.doctor_profile import (
    DoctorProfile
)

from app.auth.hash import hash_password

from app.repositories.user_repository import (
    get_user_by_email,
    create_user
)

from app.repositories.doctor_repository import (
    create_doctor_profile
)

from app.repositories.doctor_repository import (
    get_doctors_by_hospital
)

from app.repositories.doctor_repository import (
    get_doctor_by_id
)

from app.repositories.doctor_repository import (
    get_doctor_by_user_id
)

from app.core.roles import DOCTOR


def create_doctor(
    db,
    payload,
    current_user
):

    existing = get_user_by_email(
        db,
        payload.email
    )

    if existing:

        raise ValueError(
            "Doctor email already exists"
        )

    user = User(

        hospital_id=current_user[
            "hospital_id"
        ],

        full_name=payload.full_name,

        email=payload.email,

        phone=payload.phone,

        password=hash_password(
            payload.password
        ),

        role=DOCTOR
    )

    user = create_user(
        db,
        user
    )

    doctor = DoctorProfile(

        hospital_id=current_user[
            "hospital_id"
        ],

        user_id=user.id,

        specialization=payload.specialization,

        qualification=payload.qualification,

        experience_years=payload.experience_years,

        consultation_fee=payload.consultation_fee,

        registration_no=payload.registration_no,

        room_no=payload.room_no,

        start_time=payload.start_time,

        end_time=payload.end_time
    )

    doctor = create_doctor_profile(
        db,
        doctor
    )

    return doctor


def get_doctors(
    db,
    current_user
):

    return get_doctors_by_hospital(
        db,
        current_user["hospital_id"]
    )


def get_doctor(
    db,
    doctor_id,
    current_user
):

    doctor = get_doctor_by_id(
        db,
        doctor_id,
        current_user[
            "hospital_id"
        ]
    )

    if not doctor:

        raise ValueError(
            "Doctor not found"
        )

    return doctor


def update_my_profile(
    db,
    payload,
    current_user
):
    print("CURRENT USER:", current_user)
    doctor = get_doctor_by_user_id(
        db,
        current_user["user_id"]
    )
    print("DOCTOR:", doctor)
    if not doctor:

        doctor = DoctorProfile(

            hospital_id=current_user[
                "hospital_id"
            ],

            user_id=current_user[
                "user_id"
            ]
        )

        db.add(doctor)

    doctor.specialization = payload.specialization

    doctor.qualification = payload.qualification

    doctor.experience_years = payload.experience_years

    doctor.consultation_fee = payload.consultation_fee

    doctor.registration_no = payload.registration_no

    doctor.room_no = payload.room_no

    doctor.start_time = payload.start_time

    doctor.end_time = payload.end_time

    db.commit()

    db.refresh(doctor)

    return doctor


def get_my_profile(
    db,
    current_user
):

    doctor = get_doctor_by_user_id(
        db,
        current_user["user_id"]
    )

    if not doctor:

        raise ValueError(
            "Doctor profile not found"
        )

    return doctor


def update_doctor_profile(
    db,
    doctor_id,
    payload
):
    doctor = (
        db.query(User)
        .filter(
            User.id == doctor_id,
            User.role == "DOCTOR"
        )
        .first()
    )

    if not doctor:
        raise Exception("Doctor not found")

    if payload.name:
        doctor.name = payload.name

    if payload.email:
        doctor.email = payload.email

    if payload.mobile:
        doctor.mobile = payload.mobile

    profile = (
        db.query(DoctorProfile)
        .filter(
            DoctorProfile.user_id == doctor.id
        )
        .first()
    )

    if not profile:
        profile = DoctorProfile(
            user_id=doctor.id
        )
        db.add(profile)

    data = payload.model_dump(exclude_unset=True)

    for field in [
        "specialization",
        "qualification",
        "registration_no",
        "experience_years",
        "department",
        "consultation_fee",
        "gender",
        "dob",
        "address",
        "city",
        "state",
        "pincode",
    ]:
        if field in data:
            setattr(profile, field, data[field])

    db.commit()
    db.refresh(doctor)

    return {"message": "Doctor updated"}
