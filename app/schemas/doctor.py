from pydantic import (
    BaseModel,
    EmailStr
)

from datetime import time


class DoctorCreate(
    BaseModel
):

    full_name: str

    email: EmailStr

    phone: str

    password: str

    specialization: str

    qualification: str

    experience_years: int

    consultation_fee: int

    registration_no: str

    room_no: str

    start_time: time

    end_time: time


class DoctorListResponse(
    BaseModel
):

    id: int

    full_name: str

    hospital_id: int

    user_id: int

    specialization: str

    qualification: str

    experience_years: int

    consultation_fee: int

    registration_no: str

    room_no: str

    is_available: bool

    class Config:
        from_attributes = True


class DoctorProfileUpdate(
    BaseModel
):

    full_name: str

    specialization: str

    qualification: str

    experience_years: int

    consultation_fee: int

    registration_no: str

    room_no: str

    start_time: time

    end_time: time
