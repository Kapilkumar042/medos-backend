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


def get_bill_by_id(
    db,
    bill_id,
    hospital_id
):
    return db.query(
        OpdBill
    ).filter(
        OpdBill.id == bill_id,
        OpdBill.hospital_id == hospital_id
    ).first()


def get_bill_items_by_bill(
    db,
    bill_id
):
    return db.query(
        OpdBillItem
    ).filter(
        OpdBillItem.bill_id == bill_id
    ).all()
