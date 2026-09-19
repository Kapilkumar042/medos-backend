from pydantic import BaseModel


class QueueDoctorResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    specialization: str | None = None

    class Config:
        from_attributes = True


class QueuePatientResponse(BaseModel):
    id: int
    name: str
    uhid: str
    mobile: str | None = None

    class Config:
        from_attributes = True


class QueueResponse(BaseModel):
    id: int
    token_no: int
    status: str

    doctor_id: int | None
    doctor: QueueDoctorResponse | None

    opd_patient_id: int
    patient: QueuePatientResponse

    class Config:
        from_attributes = True
