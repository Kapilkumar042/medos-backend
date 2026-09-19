from app.db.base import Base
from app.db.session import engine

from app.models.hospital import Hospital
from app.models.user import User
from app.models.doctor_profile import (
    DoctorProfile
)
from app.models.lab_test import LabTest

from app.models.catalog import (
    RadiologyTest,
    Medicine,
    HospitalService,
    Department
)


def create_tables():
    Base.metadata.create_all(
        bind=engine
    )
