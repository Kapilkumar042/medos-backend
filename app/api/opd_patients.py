from fastapi import APIRouter
from fastapi import Depends

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
)
from app.schemas.opd_patient import (
    CreatePatientRequest,
)

router = APIRouter(
    prefix="/opd/patients",
    tags=["OPD Patients"]
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
    payload: CreatePatientRequest,
    db=Depends(get_db),
    current_user=Depends(get_current_user)
):
    return update_patient(
        db,
        patient_id,
        payload,
        current_user
    )
