from pydantic import BaseModel
from typing import Optional


class CreateDoctorProfileRequest(BaseModel):
    first_name: str

    last_name: Optional[str] = None

    gender: Optional[str] = None

    email: Optional[str] = None
    phone: Optional[str] = None
    alt_phone: Optional[str] = None

    specialization: Optional[str] = None
    qualification: Optional[str] = None
    registration_no: Optional[str] = None

    experience_years: Optional[int] = None

    department: Optional[str] = None
    designation: Optional[str] = None

    normal_fee: Optional[float] = None
    on_call_fee: Optional[float] = None

    emergency_fee: Optional[float] = None
    follow_up_fee: Optional[float] = None

    available_days: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    room_no: Optional[str] = None

    status: str = "Active"


class UpdateDoctorProfileRequest(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None

    gender: Optional[str] = None

    email: Optional[str] = None
    phone: Optional[str] = None
    alt_phone: Optional[str] = None

    specialization: Optional[str] = None
    qualification: Optional[str] = None
    registration_no: Optional[str] = None

    experience_years: Optional[int] = None

    department: Optional[str] = None
    designation: Optional[str] = None

    normal_fee: Optional[float] = None
    on_call_fee: Optional[float] = None

    emergency_fee: Optional[float] = None
    follow_up_fee: Optional[float] = None

    available_days: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    room_no: Optional[str] = None

    status: Optional[str] = None