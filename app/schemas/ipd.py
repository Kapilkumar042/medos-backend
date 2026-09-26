from pydantic import BaseModel
from datetime import datetime


# class AdmitNewPatientRequest(BaseModel):
#     name: str
#     mobile: str
#     gender: str | None = None
#     age: int
#     address: str | None = None

#     doctor_id: int | None = None
#     ward: str | None = None
#     room: str | None = None
#     bed_no: str | None = None
#     diagnosis: str | None = None

#     advance_amount: float = 0
#     payment_mode: str | None = None
#     admission_date: datetime | None = None


from datetime import datetime, date

class AdmissionFields(BaseModel):
    doctor_id: int | None = None
    ward: str | None = None
    room: str | None = None
    bed_no: str | None = None
    diagnosis: str | None = None
    admission_date: datetime | None = None
    status: str | None = "Admitted"

    department: str | None = None
    attendant_name: str | None = None
    emergency_contact: str | None = None
    expected_discharge_date: datetime | None = None
    notes: str | None = None
    package_name: str | None = None
    reason: str | None = None
    referral: str | None = None
    room_category: str | None = None
    insurance_policy: str | None = None
    insurer: str | None = None
    age_days: int = 0
    age_months: int = 0


class AdmitNewPatientRequest(AdmissionFields):
    name: str
    mobile: str
    gender: str | None = None
    age: int
    address: str | None = None
    dob: date | None = None
    opd_no: str | None = None

    advance_amount: float = 0
    payment_mode: str | None = None

class AdmitExistingPatientRequest(BaseModel):
    patient_id: int
    doctor_id: int | None = None
    ward: str | None = None
    room: str | None = None
    bed_no: str | None = None
    diagnosis: str | None = None
    admission_date: datetime | None = None


class AdmitFromOPDRequest(BaseModel):
    patient_id: int
    doctor_id: int | None = None
    ward: str | None = None
    room: str | None = None
    bed_no: str | None = None
    diagnosis: str | None = None
    admission_date: datetime | None = None


class UpdateIPDAdmissionRequest(BaseModel):
    name: str | None = None
    mobile: str | None = None
    gender: str | None = None
    age: int | None = None
    address: str | None = None
    dob: date | None = None

    doctor_id: int | None = None
    ward: str | None = None
    room: str | None = None
    bed_no: str | None = None
    diagnosis: str | None = None
    admission_date: datetime | None = None
    admission_type: str | None = None
    status: str | None = None

    age_days: int | None = None
    age_months: int | None = None
    attendant_name: str | None = None
    department: str | None = None
    emergency_contact: str | None = None
    expected_discharge_date: datetime | None = None
    insurance_policy: str | None = None
    insurer: str | None = None
    notes: str | None = None
    package_name: str | None = None
    reason: str | None = None
    referral: str | None = None
    room_category: str | None = None