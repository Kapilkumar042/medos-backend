from datetime import datetime

from app.models.opd_bill import OpdBill
from app.models.opd_bill_item import OpdBillItem
from app.models.opd_patient import OpdPatient
from app.models.opd_visit import OpdVisit

from app.repositories.opd_bill_repository import (
    create_bill,
    create_bill_item,
    get_bills_by_hospital,
    get_bill_by_id,
    get_bill_items_by_bill
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


def get_bill(
    db,
    bill_id,
    current_user
):
    bill = get_bill_by_id(
        db,
        bill_id,
        current_user["hospital_id"]
    )

    if not bill:
        return None

    items = get_bill_items_by_bill(
        db,
        bill.id
    )

    # attach items for convenience
    bill.items = items

    return bill


def update_opd_bill(
    db,
    bill_id,
    payload,
    current_user
):
    hospital_id = current_user["hospital_id"]

    bill = (
        db.query(OpdBill)
        .filter(
            OpdBill.id == bill_id,
            OpdBill.hospital_id == hospital_id
        )
        .first()
    )

    if not bill:
        return None

    data = payload.model_dump(
        exclude_unset=True,
        exclude={"items"}
    )

    if "patient_id" in data:
        patient = (
            db.query(OpdPatient)
            .filter(
                OpdPatient.id == data["patient_id"],
                OpdPatient.hospital_id == hospital_id
            )
            .first()
        )

        if not patient:
            raise ValueError("Patient not found")

    if "visit_id" in data and data["visit_id"] is not None:
        visit = (
            db.query(OpdVisit)
            .filter(
                OpdVisit.id == data["visit_id"],
                OpdVisit.hospital_id == hospital_id
            )
            .first()
        )

        if not visit:
            raise ValueError("Visit not found")

    for key, value in data.items():
        setattr(bill, key, value)

    if "net_amount" in data or "paid_amount" in data:
        bill.due_amount = (
            (bill.net_amount or 0)
            - (bill.paid_amount or 0)
        )

    if payload.items is not None:
        db.query(OpdBillItem).filter(
            OpdBillItem.bill_id == bill.id
        ).delete(
            synchronize_session=False
        )

        for item in payload.items:
            db.add(
                OpdBillItem(
                    bill_id=bill.id,
                    category=item.category,
                    name=item.name,
                    code=item.code,
                    qty=item.qty,
                    amount=item.amount,
                    discount=item.discount,
                    remarks=item.remarks
                )
            )

    db.commit()
    db.refresh(bill)

    bill.items = get_bill_items_by_bill(
        db,
        bill.id
    )

    return bill
