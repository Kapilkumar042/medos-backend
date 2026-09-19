from app.models.opd_queue import OpdQueue


def create_queue(
    db,
    queue
):
    db.add(queue)
    db.commit()
    db.refresh(queue)

    return queue
