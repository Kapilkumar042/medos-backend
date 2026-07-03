from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.db.session import get_db

from app.auth.dependencies import (
    get_current_user
)

from app.schemas.opd_visit import (
    CreateVisitRequest,
    VisitResponse
)

from app.services.opd_visit_service import (
    create_opd_visit,
    get_opd_visits
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
