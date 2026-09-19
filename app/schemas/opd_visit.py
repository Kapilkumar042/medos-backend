from pydantic import BaseModel
from datetime import date


class CreateVisitRequest(BaseModel):

    patient_id: int

    doctor_id: int

    department: str

    visit_date: date

    symptoms: str | None = None

    notes: str | None = None


class VisitResponse(CreateVisitRequest):

    id: int

    class Config:
        from_attributes = True


class UpdateVisitRequest(BaseModel):
    doctor_id: int | None = None
    department: str | None = None
    visit_date: date | None = None
    symptoms: str | None = None
    notes: str | None = None
