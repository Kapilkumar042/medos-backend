from app.models.opd_bill import OpdBill
from app.models.opd_bill_item import OpdBillItem


def create_bill(
    db,
    bill
):
    db.add(bill)

    db.commit()

    db.refresh(bill)

    return bill


def create_bill_item(
    db,
    item
):
    db.add(item)

    db.commit()

    db.refresh(item)

    return item


def get_bills_by_hospital(
    db,
    hospital_id
):
    return db.query(
        OpdBill
    ).filter(
        OpdBill.hospital_id == hospital_id
    ).all()
