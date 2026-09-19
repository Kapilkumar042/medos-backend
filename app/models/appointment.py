from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    Time,
    ForeignKey,
    DateTime
)
from datetime import datetime

from sqlalchemy.orm import relationship

from app.db.base import Base


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)

    hospital_id = Column(
        Integer,
        ForeignKey("hospitals.id"),
        nullable=False
    )

    opd_patient_id = Column(
        Integer,
        ForeignKey("opd_patients.id"),
        nullable=True
    )

    token = Column(Integer)

    patient_name = Column(String)
    phone = Column(String)
    blood_group = Column(String)
    gender = Column(String)
    age = Column(Integer)

    doctor_id = Column(
        Integer,
        ForeignKey("doctor_profiles.id"),
        nullable=True
    )

    department = Column(String)

    service = Column(String)
    other_service = Column(String)

    appointment_date = Column(Date)
    appointment_time = Column(Time)

    visit_type = Column(String)

    notes = Column(String)

    status = Column(
        String,
        default="Scheduled"
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    doctor = relationship(
        "DoctorProfile",
        lazy="joined"
    )
