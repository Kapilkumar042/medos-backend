from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.db.session import get_db

from app.auth.dependencies import (
    get_current_user
)

from app.models.opd_visit import OpdVisit
from app.schemas.opd_visit import (
    CreateVisitRequest,
    VisitResponse,
    UpdateVisitRequest
)

from app.services.opd_visit_service import (
    create_opd_visit,
    get_opd_visits,
    get_opd_visits_for_patient,
    update_opd_visit

)

router = APIRouter(
    prefix="/opd/visits",
    tags=["OPD Visits"]
)


@router.post(
    "",
    response_model=VisitResponse
)
def create_visit(
    payload: CreateVisitRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return create_opd_visit(
        db,
        payload,
        current_user
    )


@router.get("")
def get_visits(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return get_opd_visits(
        db,
        current_user
    )

@router.get("/patient/{patient_id}")
def get_patient_visits(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return get_opd_visits_for_patient(db, patient_id, current_user)

@router.get("/{visit_id}")
def get_visit_by_id(
    visit_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    visit = (
        db.query(OpdVisit)
        .filter(
            OpdVisit.id == visit_id,
            OpdVisit.hospital_id == current_user["hospital_id"]
        )
        .first()
    )

    if not visit:
        raise HTTPException(status_code=404, detail="Visit not found")

    return visit


@router.put(
    "/{visit_id}",
    response_model=VisitResponse
)
def update_visit(
    visit_id: int,
    payload: UpdateVisitRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    visit = update_opd_visit(
        db,
        visit_id,
        payload,
        current_user
    )

    if not visit:
        raise HTTPException(
            status_code=404,
            detail="Visit not found"
        )

    return visit
