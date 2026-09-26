from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from app.db.session import get_db

from app.auth.dependencies import (
    get_current_user
)

from app.schemas.ipd import (
    AdmitNewPatientRequest,
    AdmitExistingPatientRequest,
    AdmitFromOPDRequest,
    UpdateIPDAdmissionRequest,
)

from app.services.ipd_service import (
    admit_new_patient,
    admit_existing_patient,
    admit_from_opd,
    get_ipd_patients,
    discharge_patient,
    update_ipd_admission,
    delete_ipd_admission,
    get_ipd_patient_by_id,
)

from app.services.ipd_service import (
    discharge_patient
)

router = APIRouter(
    prefix="/ipd",
    tags=["IPD"]
)

@router.get("")
def get_ipd_patients_api(
    db=Depends(get_db),
    current_user=Depends(get_current_user)
):

    return get_ipd_patients(
        db,
        current_user
    )
@router.post(
    "/admit-new"
)
def admit_new_api(
    payload: AdmitNewPatientRequest,
    db=Depends(get_db),
    current_user=Depends(
        get_current_user
    )
):

    return admit_new_patient(
        db,
        payload,
        current_user
    )

@router.post(
    "/admit-existing"
)
def admit_existing_api(
    payload:
    AdmitExistingPatientRequest,

    db=Depends(get_db),

    current_user=Depends(
        get_current_user
    )
):

    return admit_existing_patient(
        db,
        payload,
        current_user
    )


@router.post(
    "/admit-from-opd"
)
def admit_opd_api(
    payload:
    AdmitFromOPDRequest,

    db=Depends(get_db),

    current_user=Depends(
        get_current_user
    )
):

    return admit_from_opd(
        db,
        payload,
        current_user
    )



@router.put(
    "/{admission_id}/discharge"
)
def discharge_patient_api(
    admission_id: int,
    db=Depends(get_db),
    current_user=Depends(
        get_current_user
    )
):

    admission = discharge_patient(
        db,
        admission_id,
        current_user["hospital_id"]
    )

    if not admission:
        raise HTTPException(
            status_code=404,
            detail="Admission not found"
        )

    return admission


@router.put("/{admission_id}")
def update_ipd_patient_api(
    admission_id: int,
    payload: UpdateIPDAdmissionRequest,
    db=Depends(get_db),
    current_user=Depends(get_current_user),
):
    admission = update_ipd_admission(
        db,
        admission_id,
        payload,
        current_user["hospital_id"],
    )

    if not admission:
        raise HTTPException(
            status_code=404,
            detail="IPD admission not found",
        )

    return admission


@router.delete("/{admission_id}")
def delete_ipd_patient_api(
    admission_id: int,
    db=Depends(get_db),
    current_user=Depends(get_current_user),
):
    admission = delete_ipd_admission(
        db,
        admission_id,
        current_user["hospital_id"],
    )

    if not admission:
        raise HTTPException(
            status_code=404,
            detail="IPD admission not found",
        )

    return {
        "message": "IPD patient deleted successfully",
        "admission_id": admission.id,
    }

@router.get("/{admission_id}")
def get_ipd_patient_by_id_api(
    admission_id: int,
    db=Depends(get_db),
    current_user=Depends(get_current_user),
):
    admission = get_ipd_patient_by_id(
        db,
        admission_id,
        current_user,
    )

    if not admission:
        raise HTTPException(
            status_code=404,
            detail="IPD patient not found",
        )

    return admission