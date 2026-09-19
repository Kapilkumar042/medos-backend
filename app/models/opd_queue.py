from sqlalchemy import Column, ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Date
from sqlalchemy import DateTime

from app.db.base import Base
from sqlalchemy.orm import relationship


class OpdQueue(Base):
    __tablename__ = "opd_queue"

    id = Column(
        Integer,
        primary_key=True
    )

    hospital_id = Column(
        Integer,
        nullable=False
    )

    opd_patient_id = Column(
        Integer,
        ForeignKey("opd_patients.id"),
        nullable=False
    )

    doctor_id = Column(
        Integer,
        ForeignKey("doctor_profiles.id")
    )

    token_no = Column(
        Integer,
        nullable=False
    )

    queue_date = Column(Date)

    status = Column(
        String,
        default="Waiting"
    )

    checkin_time = Column(DateTime)

    called_time = Column(DateTime)

    completed_time = Column(DateTime)

    doctor = relationship(
        "DoctorProfile",
        lazy="joined"
    )

    patient = relationship(
        "OpdPatient",
        lazy="joined",
        foreign_keys=[opd_patient_id]
    )
