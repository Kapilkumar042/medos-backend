from sqlalchemy.orm import Session

from app.models.user import User


def get_user_by_email(
    db: Session,
    email: str
):
    return (
        db.query(User)
        .filter(User.email == email)
        .first()
    )


def create_user(
    db: Session,
    user: User
):
    db.add(user)

    db.commit()

    db.refresh(user)

    return user

def get_users_by_hospital(
    db,
    hospital_id
):

    return (
        db.query(User)
        .filter(
            User.hospital_id == hospital_id
        )
        .all()
    )