from pydantic import BaseModel
from typing import Optional


class CreateDoctorProfileRequest(BaseModel):
    first_name: str
    last_name: str

    gender: str

    email: Optional[str] = None
    phone: str
    alt_phone: Optional[str] = None

    specialization: str
    qualification: str
    registration_no: str

    experience_years: int

    department: str
    designation: str

    normal_fee: float
    on_call_fee: float

    emergency_fee: Optional[float] = None
    follow_up_fee: Optional[float] = None

    available_days: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    room_no: Optional[str] = None

    status: str = "Active"


class UpdateDoctorProfileRequest(CreateDoctorProfileRequest):
    pass
