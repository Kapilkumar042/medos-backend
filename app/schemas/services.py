from pydantic import BaseModel
from typing import Optional


class CreateLabTestRequest(BaseModel):
    code: str
    test_name: str
    category: str

    price: float

    sample_type: str
    report_time: str
    method: str

    status: str = "Active"


class UpdateLabTestRequest(CreateLabTestRequest):
    pass
