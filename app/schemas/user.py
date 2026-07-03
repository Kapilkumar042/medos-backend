from pydantic import (
    BaseModel,
    EmailStr
)


class UserCreate(BaseModel):

    full_name: str

    email: EmailStr

    phone: str

    password: str

    role: str

class UserResponse(BaseModel):

    id: int

    full_name: str

    email: str

    phone: str

    role: str

    is_active: bool

    class Config:
        from_attributes = True