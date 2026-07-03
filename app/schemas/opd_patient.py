from pydantic import BaseModel
from datetime import date
from datetime import datetime


class OpdPatientCreate(BaseModel):

    abha: str | None = None

    aadhaar: str | None = None

    salutation: str | None = None

    name: str

    gender: str | None = None

    patient_type: str | None = None

    relation: str | None = None

    relative_name: str | None = None

    dob: date | None = None

    date_time: datetime | None = None

    mobile: str | None = None

    email: str | None = None

    emergency: str | None = None

    blood_group: str | None = None

    marital: str | None = None

    occupation: str | None = None

    education: str | None = None

    religion: str | None = None

    address: str | None = None

    state: str | None = None

    district: str | None = None

    city_town: str | None = None

    pincode: str | None = None

    id_proof_type: str | None = None

    id_proof_number: str | None = None


class CreatePatientRequest(BaseModel):

    name: str
    mobile: str
    gender: str
