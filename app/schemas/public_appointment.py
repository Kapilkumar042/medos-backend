from datetime import date, time

from pydantic import BaseModel


class PublicAppointmentRequest(BaseModel):
    hospital_id: int

    patient_name: str
    phone: str
    gender: str
    age: int | None = None
    blood_group: str | None = None

    doctor_id: int | None = None
    department: str | None = None

    service: str
    other_service: str | None = None

    appointment_date: date
    appointment_time: time

    visit_type: str
    notes: str | None = None
