from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from jose import JWTError, jwt
from jinja2 import Environment, FileSystemLoader

from app.auth.dependencies import get_current_user
from app.auth.jwt import ALGORITHM, SECRET_KEY
from app.db.session import get_db
from app.models.doctor_profile import DoctorProfile
from app.models.hospital import Hospital
from app.models.ipd_admission import IPDAdmission
from app.models.ipd_bill_item import IPDBillItem
from app.models.ipd_billing import IPDBill
from app.models.opd_patient import OpdPatient
from app.schemas.ipd_bill import CreateIPDBillRequest
from app.services.ipd_billing_service import create_ipd_bill, get_ipd_bills

router = APIRouter(prefix="/ipd/billing", tags=["IPD Billing"])
env = Environment(loader=FileSystemLoader("app/templates"))


def indian_datetime(value):
    if not value:
        return "-"
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return value
    return value.strftime("%d/%m/%Y %I:%M %p")

def indian_date(value):
    if not value:
        return "-"
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return value
    return value.strftime("%d/%m/%Y")

env = Environment(loader=FileSystemLoader("app/templates"))
env.filters["indian_datetime"] = indian_datetime
env.filters["indian_date"] = indian_date

def create_print_token(bill_id: int) -> str:
    payload = {
        "bill_id": bill_id,
        "purpose": "ipd_bill_print",
        "exp": datetime.now(timezone.utc) + timedelta(days=2),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def validate_print_token(token: str, bill_id: int):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        if payload.get("purpose") != "ipd_bill_print":
            raise HTTPException(status_code=403, detail="Invalid print link")

        if int(payload.get("bill_id")) != bill_id:
            raise HTTPException(status_code=403, detail="Invalid print link")

        return payload

    except JWTError:
        raise HTTPException(status_code=403, detail="Print link expired or invalid")

@router.post("")
def create_bill_api(
    payload: CreateIPDBillRequest,
    db=Depends(get_db),
    current_user=Depends(get_current_user),
):
    return create_ipd_bill(db, payload, current_user)

@router.get("")
def get_bills_api(
    db=Depends(get_db),
    current_user=Depends(get_current_user),
):
    return get_ipd_bills(db, current_user)

@router.get("/{bill_id}/share-link")
def create_ipd_bill_share_link(
    bill_id: int,
    request: Request,
    db=Depends(get_db),
    current_user=Depends(get_current_user),
):
    bill = (
        db.query(IPDBill)
        .filter(
            IPDBill.id == bill_id,
            IPDBill.hospital_id == current_user["hospital_id"],
        )
        .first()
    )

    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")

    token = create_print_token(bill.id)
    print_url = str(request.url_for("public_ipd_print_bill", bill_id=bill.id))

    return {
        "bill_id": bill.id,
        "print_url": f"{print_url}?token={token}",
        "expires_in_days": 2,
    }

@router.get(
    "/public/{bill_id}/print",
    response_class=HTMLResponse,
    name="public_ipd_print_bill",
)
def public_ipd_print_bill(
    bill_id: int,
    token: str,
    db=Depends(get_db),
):
    validate_print_token(token, bill_id)

    bill = db.query(IPDBill).filter(IPDBill.id == bill_id).first()
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")

    patient = (
        db.query(OpdPatient)
        .filter(
            OpdPatient.id == bill.patient_id,
            OpdPatient.hospital_id == bill.hospital_id,
        )
        .first()
    )

    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    admission = (
        db.query(IPDAdmission)
        .filter(
            IPDAdmission.id == bill.admission_id,
            IPDAdmission.hospital_id == bill.hospital_id,
        )
        .first()
    )

    if not admission:
        raise HTTPException(status_code=404, detail="Admission not found")

    hospital = (
        db.query(Hospital)
        .filter(Hospital.id == bill.hospital_id)
        .first()
    )

    doctor = None
    if admission.doctor_id:
        doctor = (
            db.query(DoctorProfile)
            .filter(
                DoctorProfile.id == admission.doctor_id,
                DoctorProfile.hospital_id == bill.hospital_id,
            )
            .first()
        )

    items = (
        db.query(IPDBillItem)
        .filter(IPDBillItem.bill_id == bill.id)
        .all()
    )

    template = env.get_template("ipd_bill.html")

    html = template.render(
        bill=bill,
        patient=patient,
        admission=admission,
        doctor=doctor,
        hospital=hospital,
        items=items,
        advance_paid=bill.advance_paid,
    )

    return HTMLResponse(content=html)

@router.get("/{bill_id}/print", response_class=HTMLResponse)
def print_ipd_bill(
    bill_id: int,
    db=Depends(get_db),
    current_user=Depends(get_current_user),
):
    hospital_id = current_user["hospital_id"]

    bill = (
        db.query(IPDBill)
        .filter(
            IPDBill.id == bill_id,
            IPDBill.hospital_id == hospital_id,
        )
        .first()
    )

    if not bill:
        raise HTTPException(status_code=404, detail=f"IPD Bill {bill_id} not found")

    patient = (
        db.query(OpdPatient)
        .filter(
            OpdPatient.id == bill.patient_id,
            OpdPatient.hospital_id == hospital_id,
        )
        .first()
    )

    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found for this bill")

    admission = (
        db.query(IPDAdmission)
        .filter(
            IPDAdmission.id == bill.admission_id,
            IPDAdmission.hospital_id == hospital_id,
        )
        .first()
    )

    if not admission:
        raise HTTPException(status_code=404, detail="Admission not found for this bill")

    hospital = db.query(Hospital).filter(Hospital.id == hospital_id).first()

    doctor = None
    if admission.doctor_id:
        doctor = (
            db.query(DoctorProfile)
            .filter(
                DoctorProfile.id == admission.doctor_id,
                DoctorProfile.hospital_id == hospital_id,
            )
            .first()
        )

    items = (
        db.query(IPDBillItem)
        .filter(IPDBillItem.bill_id == bill.id)
        .all()
    )

    template = env.get_template("ipd_bill.html")

    html = template.render(
        bill=bill,
        patient=patient,
        admission=admission,
        doctor=doctor,
        hospital=hospital,
        items=items,
        advance_paid=bill.advance_paid,
    )

    return HTMLResponse(content=html)