from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Date
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from datetime import datetime

from app.db.base import Base


class OpdPatient(Base):

    __tablename__ = "opd_patients"

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

    uhid = Column(String, nullable=False)

    abha = Column(String)

    aadhaar = Column(String)

    opd_no = Column(String, nullable=False)

    salutation = Column(String)

    name = Column(String, nullable=False)

    gender = Column(String)

    patient_type = Column(String)

    relation = Column(String)

    relative_name = Column(String)

    dob = Column(Date)

    date_time = Column(DateTime)

    mobile = Column(String)

    email = Column(String)

    emergency = Column(String)

    blood_group = Column(String)

    marital = Column(String)

    occupation = Column(String)

    education = Column(String)

    religion = Column(String)

    address = Column(String)

    state = Column(String)

    district = Column(String)

    city_town = Column(String)

    pincode = Column(String)

    id_proof_type = Column(String)

    id_proof_number = Column(String)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )
