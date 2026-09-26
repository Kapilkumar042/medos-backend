from pydantic import BaseModel


class CreateIPDPaymentRequest(BaseModel):

    amount: float

    payment_mode: str

    remarks: str | None = None