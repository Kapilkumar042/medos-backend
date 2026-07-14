from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    ForeignKey,
    DateTime
)
from datetime import datetime

from app.db.base import Base


class DoctorProfile(Base):
    __tablename__ = "doctor_profiles"

    id = Column(Integer, primary_key=True, index=True)

    hospital_id = Column(
        Integer,
        ForeignKey("hospitals.id"),
        nullable=False
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )

    doctor_code = Column(String, unique=True)

    first_name = Column(String)
    last_name = Column(String)

    gender = Column(String)

    email = Column(String)
    phone = Column(String)
    alt_phone = Column(String)

    specialization = Column(String)
    qualification = Column(String)
    registration_no = Column(String)

    experience_years = Column(Integer)

    department = Column(String)
    designation = Column(String)

    normal_fee = Column(Float)
    on_call_fee = Column(Float)
    emergency_fee = Column(Float)
    follow_up_fee = Column(Float)

    available_days = Column(String)
    start_time = Column(String)
    end_time = Column(String)
    room_no = Column(String)

    status = Column(String, default="Active")

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
