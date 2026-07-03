from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey,
    Time
)
from sqlalchemy.orm import relationship

from app.db.base import Base


class DoctorProfile(Base):

    __tablename__ = "doctor_profiles"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    hospital_id = Column(
        Integer,
        ForeignKey("hospitals.id"),
        nullable=False
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        unique=True,
        nullable=False
    )

    specialization = Column(
        String(255),
        nullable=False
    )

    qualification = Column(
        String(255)
    )

    experience_years = Column(
        Integer,
        default=0
    )

    consultation_fee = Column(
        Integer,
        default=0
    )

    registration_no = Column(
        String(100)
    )

    room_no = Column(
        String(50)
    )

    start_time = Column(
        Time
    )

    end_time = Column(
        Time
    )

    is_available = Column(
        Boolean,
        default=True
    )

    user = relationship("User")

    @property
    def full_name(self):
        return self.user.full_name if self.user else None
