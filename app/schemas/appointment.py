from pydantic import BaseModel
from typing import Optional
from datetime import date, time


class CreateAppointmentRequest(BaseModel):
    patient_name: str
    phone: str
    blood_group: Optional[str] = None
    gender: str
    age: Optional[int] = None

    doctor_id: Optional[int] = None
    department: Optional[str] = None

    service: str
    other_service: Optional[str] = None

    appointment_date: date
    appointment_time: time

    visit_type: str
    notes: Optional[str] = None


class UpdateAppointmentStatusRequest(BaseModel):
    status: str
