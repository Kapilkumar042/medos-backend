from fastapi import APIRouter
from fastapi import Depends
from fastapi.responses import HTMLResponse

from sqlalchemy.orm import Session

from app.db.session import get_db

from app.auth.dependencies import (
    get_current_user
)

from jinja2 import Environment
from jinja2 import FileSystemLoader
from app.models.opd_bill import OpdBill
from app.models.opd_patient import OpdPatient
from app.models.hospital import Hospital
from app.models.opd_bill_item import OpdBillItem
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, Request
from jose import jwt, JWTError

from app.auth.jwt import SECRET_KEY, ALGORITHM

from app.schemas.opd_bill import (
    CreateBillRequest,
    UpdateBillRequest
)

from app.services.opd_bill_service import (
    create_opd_bill,
    get_bills,
    get_bill,
    update_opd_bill
)

router = APIRouter(
    prefix="/opd/bills",
    tags=["OPD Billing"]
)

env = Environment(
    loader=FileSystemLoader(
        "app/templates"
    )
)


def create_print_token(bill_id: int) -> str:
    payload = {
        "bill_id": bill_id,
        "purpose": "public_bill_print",
        "exp": datetime.now(timezone.utc) + timedelta(days=2),
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


def validate_print_token(
    token: str,
    bill_id: int
):
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        if payload.get("purpose") != "public_bill_print":
            raise HTTPException(
                status_code=403,
                detail="Invalid print link"
            )

        if int(payload.get("bill_id")) != bill_id:
            raise HTTPException(
                status_code=403,
                detail="Invalid print link"
            )

        return payload

    except JWTError:
        raise HTTPException(
            status_code=403,
            detail="Print link expired or invalid"
        )


@router.get("/{bill_id}/share-link")
def create_bill_share_link(
    bill_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    bill = (
        db.query(OpdBill)
        .filter(
            OpdBill.id == bill_id,
            OpdBill.hospital_id == current_user["hospital_id"]
        )
        .first()
    )

    if not bill:
        raise HTTPException(
            status_code=404,
            detail="Bill not found"
        )

    token = create_print_token(bill.id)

    print_url = str(
        request.url_for(
            "public_print_bill",
            bill_id=bill.id
        )
    )

    print_url = f"{print_url}?token={token}"

    return {
        "bill_id": bill.id,
        "print_url": print_url,
        "expires_in_days": 2
    }


@router.get(
    "/public/{bill_id}/print",
    response_class=HTMLResponse,
    name="public_print_bill"
)
def public_print_bill(
    bill_id: int,
    token: str,
    db: Session = Depends(get_db)
):
    validate_print_token(
        token,
        bill_id
    )

    bill = (
        db.query(OpdBill)
        .filter(
            OpdBill.id == bill_id
        )
        .first()
    )

    if not bill:
        raise HTTPException(
            status_code=404,
            detail="Bill not found"
        )

    patient = (
        db.query(OpdPatient)
        .filter(
            OpdPatient.id == bill.patient_id,
            OpdPatient.hospital_id == bill.hospital_id
        )
        .first()
    )

    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    hospital = (
        db.query(Hospital)
        .filter(
            Hospital.id == bill.hospital_id
        )
        .first()
    )

    items = (
        db.query(OpdBillItem)
        .filter(
            OpdBillItem.bill_id == bill.id
        )
        .all()
    )

    template = env.get_template(
        "opd_bill.html"
    )

    html = template.render(
        bill=bill,
        patient=patient,
        hospital=hospital,
        items=items
    )

    return HTMLResponse(
        content=html
    )


@router.get(
    "/{bill_id}/print",
    response_class=HTMLResponse
)
def print_bill(
    bill_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    hospital_id = current_user["hospital_id"]

    bill = (
        db.query(OpdBill)
        .filter(
            OpdBill.id == bill_id,
            OpdBill.hospital_id == hospital_id
        )
        .first()
    )

    if not bill:
        raise HTTPException(
            status_code=404,
            detail=f"Bill {bill_id} not found"
        )

    patient = (
        db.query(OpdPatient)
        .filter(
            OpdPatient.id == bill.patient_id,
            OpdPatient.hospital_id == hospital_id
        )
        .first()
    )

    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Patient not found for this bill"
        )

    hospital = (
        db.query(Hospital)
        .filter(
            Hospital.id == hospital_id
        )
        .first()
    )

    items = (
        db.query(OpdBillItem)
        .filter(
            OpdBillItem.bill_id == bill.id
        )
        .all()
    )

    template = env.get_template("opd_bill.html")

    html = template.render(
        bill=bill,
        patient=patient,
        hospital=hospital,
        items=items
    )

    return HTMLResponse(content=html)


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


@router.get("/{bill_id}")
def fetch_bill(

    bill_id: int,

    db: Session = Depends(get_db),

    current_user=Depends(
        get_current_user
    )
):

    bill = get_bill(
        db,
        bill_id,
        current_user
    )

    if not bill:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Bill not found")

    return bill


@router.put("/{bill_id}")
def update_bill(
    bill_id: int,
    payload: UpdateBillRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    try:
        bill = update_opd_bill(
            db,
            bill_id,
            payload,
            current_user
        )
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    if not bill:
        raise HTTPException(
            status_code=404,
            detail="Bill not found"
        )

    return bill
