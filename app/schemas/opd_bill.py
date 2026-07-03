from pydantic import BaseModel
from typing import List
from decimal import Decimal


class BillItemRequest(BaseModel):

    category: str
    name: str
    code: str | None = None

    qty: int

    amount: Decimal

    discount: Decimal = 0

    remarks: str | None = None


class CreateBillRequest(BaseModel):

    patient_id: int

    visit_id: int | None = None

    total_amount: Decimal

    total_discount: Decimal

    net_amount: Decimal

    paid_amount: Decimal

    payment_mode: str

    remark: str | None = None

    items: List[BillItemRequest]
