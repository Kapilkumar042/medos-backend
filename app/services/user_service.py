from app.models.user import User

from app.auth.hash import hash_password

from app.repositories.user_repository import (
    create_user,
    get_user_by_email
)
from app.repositories.user_repository import (
    get_users_by_hospital
)


def create_staff_user(
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
            "Email already exists"
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

        role=payload.role
    )

    return create_user(
        db,
        user
    )

def get_staff_users(
    db,
    current_user
):

    return get_users_by_hospital(
        db,
        current_user["hospital_id"]
    )