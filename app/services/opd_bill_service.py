from datetime import datetime

from app.models.opd_bill import OpdBill
from app.models.opd_bill_item import OpdBillItem

from app.repositories.opd_bill_repository import (
    create_bill,
    create_bill_item,
    get_bills_by_hospital
)


def generate_bill_no(
    hospital_id
):
    date = datetime.now().strftime(
        "%Y%m%d"
    )

    return f"BILL-{hospital_id}-{date}-{int(datetime.now().timestamp())}"


def create_opd_bill(
    db,
    payload,
    current_user
):

    due_amount = (
        payload.net_amount
        - payload.paid_amount
    )

    bill = OpdBill(

        hospital_id=current_user[
            "hospital_id"
        ],

        patient_id=payload.patient_id,

        visit_id=payload.visit_id,

        bill_no=generate_bill_no(
            current_user["hospital_id"]
        ),

        total_amount=payload.total_amount,

        total_discount=payload.total_discount,

        net_amount=payload.net_amount,

        paid_amount=payload.paid_amount,

        due_amount=due_amount,

        payment_mode=payload.payment_mode,

        remark=payload.remark
    )

    bill = create_bill(
        db,
        bill
    )

    for item in payload.items:

        bill_item = OpdBillItem(

            bill_id=bill.id,

            category=item.category,

            name=item.name,

            code=item.code,

            qty=item.qty,

            amount=item.amount,

            discount=item.discount,

            remarks=item.remarks
        )

        create_bill_item(
            db,
            bill_item
        )

    return bill


def get_bills(
    db,
    current_user
):

    return get_bills_by_hospital(
        db,
        current_user["hospital_id"]
    )
