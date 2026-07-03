from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Date
)

from app.db.base import Base


class OpdVisit(Base):

    __tablename__ = "opd_visits"

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

    patient_id = Column(
        Integer,
        ForeignKey("opd_patients.id"),
        nullable=False
    )

    doctor_id = Column(
        Integer,
        ForeignKey("doctor_profiles.id"),
        nullable=False
    )

    department = Column(
        String,
        nullable=False
    )

    visit_date = Column(
        Date,
        nullable=False
    )

    symptoms = Column(
        String
    )

    notes = Column(
        String
    )
