from pydantic import BaseModel
from typing import Optional


class CreateLabTestRequest(BaseModel):
    code: str | None = None
    test_name: str
    category: str | None = None

    price: float

    sample_type: str | None = None
    report_time: str | None = None
    method: str | None = None

    status: str = "Active"


class UpdateLabTestRequest(CreateLabTestRequest):
    pass
