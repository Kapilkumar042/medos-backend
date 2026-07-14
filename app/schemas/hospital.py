from pydantic import BaseModel, EmailStr


class HospitalRegister(BaseModel):
    hospital_name: str
    hospital_email: EmailStr
    phone: str
    # admin_name: str
    # admin_email: EmailStr
    password: str
    modules: list[str]


class HospitalLogin(BaseModel):
    email: EmailStr
    password: str
