from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.db.session import get_db

from app.auth.dependencies import (
    get_current_user
)

from app.schemas.ipd_payment import (
    CreateIPDPaymentRequest
)

from app.services.ipd_payment_service import (
    add_payment,
    get_payments
)

router = APIRouter(
    prefix="/ipd",
    tags=["IPD Payments"]
)


@router.post(
    "/{admission_id}/payment"
)
def create_payment(

    admission_id: int,

    payload: CreateIPDPaymentRequest,

    db: Session = Depends(get_db),

    current_user=Depends(
        get_current_user
    )
):

    return add_payment(
        db,
        admission_id,
        payload,
        current_user
    )


@router.get(
    "/{admission_id}/payments"
)
def payment_history(

    admission_id: int,

    db: Session = Depends(get_db),

    current_user=Depends(
        get_current_user
    )
):

    return get_payments(
        db,
        admission_id,
        current_user["hospital_id"]
    )