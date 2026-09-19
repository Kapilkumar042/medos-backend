from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.lab_test_service import import_lab_tests

from app.auth.dependencies import get_current_user

from app.schemas.lab_test import (
    CreateLabTestRequest,
    UpdateLabTestRequest
)

from app.services.lab_test_service import (
    create_lab_test,
    get_lab_tests,
    update_lab_test
)

router = APIRouter(
    prefix="/lab",
    tags=["Lab Tests"]
)


@router.post("")
def create_lab_test_api(
    payload: CreateLabTestRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return create_lab_test(
        db,
        payload,
        current_user
    )


@router.get("")
def get_lab_tests_api(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return get_lab_tests(
        db,
        current_user["hospital_id"]
    )


@router.put("/{test_id}")
def update_lab_test_api(
    test_id: int,
    payload: UpdateLabTestRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return update_lab_test(
        db,
        test_id,
        payload,
        current_user["hospital_id"]
    )


@router.post("/import")
def import_lab_tests_api(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return import_lab_tests(
        db,
        file,
        current_user
    )
