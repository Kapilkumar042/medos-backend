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
