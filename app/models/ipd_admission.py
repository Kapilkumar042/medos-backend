from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey

from app.db.base import Base


class IPDAdmission(Base):
    __tablename__ = "ipd_admissions"

    id = Column(
        Integer,
        primary_key=True
    )

    hospital_id = Column(
        Integer,
        nullable=False
    )

    uhid = Column(
        String,
        nullable=False
    )

    patient_id = Column(
        Integer,
        ForeignKey("opd_patients.id")
    )

    doctor_id = Column(
        Integer,
        ForeignKey("doctor_profiles.id")
    )

    admission_no = Column(
        String,
        unique=True
    )

    name = Column(String)

    ward = Column(String)

    room = Column(String)

    bed_no = Column(String)

    diagnosis = Column(String)
    department = Column(String)
    attendant_name = Column(String)
    emergency_contact = Column(String)
    expected_discharge_date = Column(DateTime)
    notes = Column(String)
    package_name = Column(String)
    reason = Column(String)
    referral = Column(String)
    room_category = Column(String)
    insurance_policy = Column(String)
    insurer = Column(String)
    age_days = Column(Integer, default=0)
    age_months = Column(Integer, default=0)

    admission_type = Column(
        String
    )  # New | Existing | OPD

    status = Column(
        String,
        default="Admitted"
    )

    admission_date = Column(
        DateTime
    )

    discharge_date = Column(
        DateTime
    )
