from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from app.schemas.opd_queue import QueueResponse

from sqlalchemy.orm import Session

from app.db.session import get_db

from app.models.opd_queue import OpdQueue

from app.auth.dependencies import get_current_user

from app.services.opd_queue_service import (
    get_waiting_queue,
    call_token,
    start_consultation,
    complete_consultation,
    requeue_token
)

router = APIRouter(
    prefix="/api/opd-queue",
    tags=["OPD Queue"]
)


@router.get(
    "",
    response_model=list[QueueResponse]
)
def get_queue_api(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return get_waiting_queue(
        db,
        current_user["hospital_id"]
    )


@router.put("/{queue_id}/call")
def call_queue_token(
    queue_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    queue = call_token(
        db,
        queue_id,
        current_user["hospital_id"]
    )

    if not queue:
        raise HTTPException(
            status_code=404,
            detail="Queue record not found"
        )

    return queue


@router.put("/{queue_id}/consultation")
def start_queue_consultation(
    queue_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    queue = start_consultation(
        db,
        queue_id,
        current_user["hospital_id"]
    )

    if not queue:
        raise HTTPException(
            status_code=404,
            detail="Queue record not found"
        )

    return queue


@router.put("/{queue_id}/complete")
def complete_queue_consultation(
    queue_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    queue = complete_consultation(
        db,
        queue_id,
        current_user["hospital_id"]
    )

    if not queue:
        raise HTTPException(
            status_code=404,
            detail="Queue record not found"
        )

    return queue


@router.put("/{queue_id}/skip")
def skip_queue_token(
    queue_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    queue = (
        db.query(OpdQueue)
        .filter(
            OpdQueue.id == queue_id,
            OpdQueue.hospital_id == current_user["hospital_id"]
        )
        .first()
    )

    if not queue:
        raise HTTPException(
            status_code=404,
            detail="Queue record not found"
        )

    queue.status = "Skipped"

    db.commit()
    db.refresh(queue)

    return queue


@router.put("/{queue_id}/cancel")
def cancel_queue_token(
    queue_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    queue = (
        db.query(OpdQueue)
        .filter(
            OpdQueue.id == queue_id,
            OpdQueue.hospital_id == current_user["hospital_id"]
        )
        .first()
    )

    if not queue:
        raise HTTPException(
            status_code=404,
            detail="Queue record not found"
        )

    queue.status = "Cancelled"

    db.commit()
    db.refresh(queue)

    return queue


@router.put("/{queue_id}/requeue")
def requeue_queue_token(
    queue_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    queue = requeue_token(
        db,
        queue_id,
        current_user["hospital_id"]
    )

    if not queue:
        raise HTTPException(
            status_code=404,
            detail="Queue record not found"
        )

    return queue
