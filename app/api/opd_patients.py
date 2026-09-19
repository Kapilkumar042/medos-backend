from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi.responses import HTMLResponse
from jinja2 import Environment, FileSystemLoader

from app.models.opd_patient import OpdPatient
from app.models.hospital import Hospital
from app.models.opd_bill import OpdBill
from app.models.opd_bill_item import OpdBillItem

from app.db.session import get_db

from app.auth.dependencies import (
    get_current_user
)

from app.schemas.opd_patient import (
    OpdPatientCreate
)

from app.services.opd_patient_service import (
    register_patient,
    get_patients,
    get_patient,
    update_patient
)
from app.schemas.opd_patient import (
    CreatePatientRequest,
)

router = APIRouter(
    prefix="/opd/patients",
    tags=["OPD Patients"]
)
env = Environment(
    loader=FileSystemLoader("app/templates")
)


@router.post("")
def create_patient_api(
    payload: OpdPatientCreate,
    db=Depends(get_db),
    current_user=Depends(
        get_current_user
    )
):

    return register_patient(
        db,
        payload,
        current_user
    )


@router.get("")
def get_patients_api(
    db=Depends(get_db),
    current_user=Depends(
        get_current_user
    )
):

    return get_patients(
        db,
        current_user
    )


@router.get(
    "/{patient_id}/print",
    response_class=HTMLResponse
)
def print_patient(
    patient_id: int,
    db=Depends(get_db),
    current_user=Depends(get_current_user)
):
    hospital_id = current_user["hospital_id"]

    patient = (
        db.query(OpdPatient)
        .filter(
            OpdPatient.id == patient_id,
            OpdPatient.hospital_id == hospital_id
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
            Hospital.id == hospital_id
        )
        .first()
    )

    # Get the latest bill for this patient
    bill = (
        db.query(OpdBill)
        .filter(
            OpdBill.patient_id == patient.id,
            OpdBill.hospital_id == hospital_id
        )
        .order_by(
            OpdBill.id.desc()
        )
        .first()
    )

    items = []

    if bill:
        items = (
            db.query(OpdBillItem)
            .filter(
                OpdBillItem.bill_id == bill.id
            )
            .all()
        )

    template = env.get_template(
        "opd_patient.html"
    )

    html = template.render(
        patient=patient,
        hospital=hospital,
        bill=bill,
        items=items
    )

    return HTMLResponse(
        content=html
    )


@router.get("/{patient_id}")
def get_patient_api(
    patient_id: int,
    db=Depends(get_db),
    current_user=Depends(
        get_current_user
    )
):

    return get_patient(
        db,
        patient_id,
        current_user
    )


@router.put(
    "/{patient_id}"
)
def update_patient_api(
    patient_id: int,
    payload: OpdPatientCreate,
    db=Depends(get_db),
    current_user=Depends(get_current_user)
):
    return update_patient(
        db,
        patient_id,
        payload,
        current_user
    )
