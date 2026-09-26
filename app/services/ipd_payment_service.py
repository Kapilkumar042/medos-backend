from app.models.ipd_payment import IPDPayment


def add_payment(
    db,
    admission_id,
    payload,
    current_user
):

    payment = IPDPayment(

        hospital_id=current_user[
            "hospital_id"
        ],

        admission_id=admission_id,

        amount=payload.amount,

        payment_mode=payload.payment_mode,

        remarks=payload.remarks
    )

    db.add(payment)

    db.commit()

    db.refresh(payment)

    return payment


def get_payments(
    db,
    admission_id,
    hospital_id
):

    return (
        db.query(IPDPayment)
        .filter(
            IPDPayment.admission_id == admission_id,
            IPDPayment.hospital_id == hospital_id
        )
        .all()
    )