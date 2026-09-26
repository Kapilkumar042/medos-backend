from datetime import datetime

from sqlalchemy import func

from app.models.ipd_payment import (
    IPDPayment
)

from app.models.ipd_billing import (
    IPDBill
)

from app.models.ipd_bill_item import (
    IPDBillItem
)


def generate_bill_no(
    hospital_id
):

    return (
        f"IPDBILL-"
        f"{hospital_id}-"
        f"{int(datetime.now().timestamp())}"
    )


def create_ipd_bill(
    db,
    payload,
    current_user
):

    hospital_id = current_user["hospital_id"]

    total_amount = float(payload.total_amount or 0)
    total_discount = float(payload.discount_amount or 0)

    advance_paid = (
        db.query(func.coalesce(func.sum(IPDPayment.amount), 0))
        .filter(
            IPDPayment.admission_id == payload.admission_id,
            IPDPayment.hospital_id == hospital_id,
            IPDPayment.payment_type == "Advance"
        )
        .scalar()
        or 0
    )

    # amount_after_discount = total_amount - total_discount
    # net_payable = max(amount_after_discount - advance_paid, 0)
    # paid_amount = payload.paid_amount or 0
    # due_amount = max(net_payable - paid_amount, 0)
    net_payable = float(payload.net_amount-advance_paid or 0)
    paid_amount = float(payload.paid_amount or 0)
    due_amount = max(net_payable - paid_amount, 0)

    bill = IPDBill(
        hospital_id=hospital_id,
        admission_id=payload.admission_id,
        patient_id=payload.patient_id,
        bill_no=generate_bill_no(hospital_id),
        bill_date=payload.bill_date or datetime.utcnow(),
        total_amount=total_amount,
        discount_amount=total_discount,
        advance_paid=advance_paid,
        net_amount=net_payable,
        paid_amount=paid_amount,
        due_amount=due_amount,
        payment_mode=payload.payment_mode,
        remark=payload.remark
    )

    db.add(bill)
    db.commit()
    db.refresh(bill)

    for item in payload.items:
        bill_item = IPDBillItem(
            bill_id=bill.id,
            category=item.category,
            name=item.name,
            qty=item.qty,
            rate=item.rate,
            amount=item.amount,
            discount=item.discount,
            remarks=item.remarks
        )
        db.add(bill_item)

    db.commit()
    db.refresh(bill)

    return bill

def get_ipd_bills(
    db,
    current_user
):

    return (
        db.query(
            IPDBill
        )
        .filter(
            IPDBill.hospital_id
            ==
            current_user[
                "hospital_id"
            ]
        )
        .order_by(
            IPDBill.id.desc()
        )
        .all()
    )


def get_ipd_bill(
    db,
    bill_id,
    current_user
):

    return (
        db.query(
            IPDBill
        )
        .filter(
            IPDBill.id
            == bill_id,

            IPDBill.hospital_id
            ==
            current_user[
                "hospital_id"
            ]
        )
        .first()
    )