from datetime import date
from datetime import datetime

from app.models.opd_queue import OpdQueue


def generate_token(
    db,
    hospital_id
):
    count = (
        db.query(OpdQueue)
        .filter(
            OpdQueue.hospital_id == hospital_id,
            OpdQueue.queue_date == date.today()
        )
        .count()
    )

    return count + 1


def add_to_queue(
    db,
    patient_id,
    doctor_id,
    hospital_id
):
    queue = OpdQueue(
        hospital_id=hospital_id,
        opd_patient_id=patient_id,
        doctor_id=doctor_id,
        token_no=generate_token(
            db,
            hospital_id
        ),
        queue_date=date.today(),
        status="Waiting",
        checkin_time=datetime.now()
    )

    print("Queue Doctor ID:", doctor_id)
    db.add(queue)
    db.commit()
    db.refresh(queue)

    return queue


def get_waiting_queue(
    db,
    hospital_id
):
    return (
        db.query(OpdQueue)
        .filter(
            OpdQueue.hospital_id == hospital_id
        )
        .order_by(
            OpdQueue.token_no.asc()
        )
        .all()
    )


def call_token(
    db,
    queue_id,
    hospital_id
):
    queue = (
        db.query(OpdQueue)
        .filter(
            OpdQueue.id == queue_id,
            OpdQueue.hospital_id == hospital_id
        )
        .first()
    )

    if not queue:
        return None

    queue.status = "Called"
    queue.called_time = datetime.now()

    db.commit()
    db.refresh(queue)

    return queue


def start_consultation(
    db,
    queue_id,
    hospital_id
):
    queue = (
        db.query(OpdQueue)
        .filter(
            OpdQueue.id == queue_id,
            OpdQueue.hospital_id == hospital_id
        )
        .first()
    )

    if not queue:
        return None

    queue.status = "In Consultation"

    db.commit()
    db.refresh(queue)

    return queue


def complete_consultation(
    db,
    queue_id,
    hospital_id
):
    queue = (
        db.query(OpdQueue)
        .filter(
            OpdQueue.id == queue_id,
            OpdQueue.hospital_id == hospital_id
        )
        .first()
    )

    if not queue:
        return None

    queue.status = "Completed"
    queue.completed_time = datetime.now()

    db.commit()
    db.refresh(queue)

    return queue


def skip_token(
    db,
    queue_id,
    hospital_id
):
    queue = (
        db.query(OpdQueue)
        .filter(
            OpdQueue.id == queue_id,
            OpdQueue.hospital_id == hospital_id
        )
        .first()
    )

    if not queue:
        return None

    queue.status = "Skipped"

    db.commit()
    db.refresh(queue)

    return queue


def cancel_token(
    db,
    queue_id,
    hospital_id
):
    queue = (
        db.query(OpdQueue)
        .filter(
            OpdQueue.id == queue_id,
            OpdQueue.hospital_id == hospital_id
        )
        .first()
    )

    if not queue:
        return None

    queue.status = "Cancelled"

    db.commit()
    db.refresh(queue)

    return queue


def requeue_token(
    db,
    queue_id,
    hospital_id
):
    queue = (
        db.query(OpdQueue)
        .filter(
            OpdQueue.id == queue_id,
            OpdQueue.hospital_id == hospital_id
        )
        .first()
    )

    if not queue:
        return None

    queue.status = "Waiting"

    db.commit()
    db.refresh(queue)

    return queue
