from pydantic import BaseModel
from typing import List
from typing import Optional
from datetime import datetime

class IPDBillItemRequest(
    BaseModel
):

    category: str

    name: str

    qty: float

    rate: float

    amount: float

    discount: float = 0

    remarks: Optional[str] = None


class CreateIPDBillRequest(
    BaseModel
):

    admission_id: int

    patient_id: int

    total_amount: float

    discount_amount: float

    net_amount: float

    paid_amount: float

    payment_mode: str

    remark: Optional[str] = None
    bill_date: datetime | None = None

    items: List[
        IPDBillItemRequest
    ]