from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.db.session import get_db

from app.auth.dependencies import (
    get_current_user
)

from app.schemas.opd_bill import (
    CreateBillRequest
)

from app.services.opd_bill_service import (
    create_opd_bill,
    get_bills
)

router = APIRouter(
    prefix="/opd/bills",
    tags=["OPD Billing"]
)


@router.post("")
def create_bill(

    payload: CreateBillRequest,

    db: Session = Depends(get_db),

    current_user=Depends(
        get_current_user
    )
):

    return create_opd_bill(
        db,
        payload,
        current_user
    )


@router.get("")
def list_bills(

    db: Session = Depends(get_db),

    current_user=Depends(
        get_current_user
    )
):

    return get_bills(
        db,
        current_user
    )
