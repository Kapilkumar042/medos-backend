from datetime import datetime
from collections import defaultdict

from sqlalchemy import func

from app.models.catalog import Medicine
from app.models.shared_catalog import HospitalCatalogOverride, MedicineCatalogTemplate
from app.models.opd_bill import OpdBill
from app.models.opd_bill_item import OpdBillItem
from app.models.opd_patient import OpdPatient
from app.models.opd_visit import OpdVisit

from app.repositories.opd_bill_repository import (
    get_bills_by_hospital,
    get_bill_by_id,
    get_bill_items_by_bill
)


def _is_medicine_item(item):
    return (item.category or "").strip().casefold() in {"medicine", "medicines", "drug", "pharmacy"}


def _by_code_then_name(query, model, item):
    if item.code:
        match = query.filter(model.code == item.code).first()
        if match is not None:
            return match
    if item.name:
        return query.filter(func.lower(model.name) == item.name.strip().lower()).first()
    return None


def _apply_medicine_stock(db, hospital_id, items, direction, quantity_overrides=None):
    quantity_overrides = quantity_overrides or {}
    aggregated = {}
    for item in items:
        if not _is_medicine_item(item):
            continue
        key = (item.code or "").strip().casefold() or item.name.strip().casefold()
        if key in aggregated:
            existing_item, existing_quantity = aggregated[key]
            aggregated[key] = (
                existing_item,
                existing_quantity + (quantity_overrides.get(id(item), item.qty) or 0),
            )
        else:
            aggregated[key] = (
                item,
                quantity_overrides.get(id(item), item.qty) or 0,
            )

    for item, quantity in aggregated.values():
        query = db.query(Medicine).filter(Medicine.hospital_id == hospital_id)
        medicine = _by_code_then_name(query.with_for_update(), Medicine, item)
        if medicine is not None:
            available = medicine.stock or 0
            if direction < 0 and available < quantity:
                raise ValueError(
                    f"Insufficient stock for {medicine.name}: available {available}, requested {quantity}"
                )
            medicine.stock = available + (direction * quantity)
            continue

        template = _by_code_then_name(
            db.query(MedicineCatalogTemplate).with_for_update(),
            MedicineCatalogTemplate,
            item,
        )
        if template is None:
            custom_query = db.query(HospitalCatalogOverride).filter(
                HospitalCatalogOverride.hospital_id == hospital_id,
                HospitalCatalogOverride.kind == "medicine",
                HospitalCatalogOverride.template_id.is_(None),
            )
            custom_medicine = _by_code_then_name(
                custom_query.with_for_update(),
                HospitalCatalogOverride,
                item,
            )
            if custom_medicine is None:
                raise ValueError(f"Medicine not found in this hospital: {item.name}")

            available = custom_medicine.stock or 0
            if direction < 0 and available < quantity:
                raise ValueError(
                    f"Insufficient stock for {custom_medicine.name}: "
                    f"available {available}, requested {quantity}"
                )
            custom_medicine.stock = available + (direction * quantity)
            custom_medicine.overridden_fields = sorted(
                set(custom_medicine.overridden_fields or []) | {"stock"}
            )
            continue

        override = db.query(HospitalCatalogOverride).filter(
            HospitalCatalogOverride.hospital_id == hospital_id,
            HospitalCatalogOverride.kind == "medicine",
            HospitalCatalogOverride.template_id == template.id,
        ).with_for_update().first()
        if override is None:
            override = HospitalCatalogOverride(
                hospital_id=hospital_id,
                kind="medicine",
                template_id=template.id,
                name=template.name,
                code=template.code,
                stock=template.stock or 0,
                overridden_fields=["stock"],
            )
            db.add(override)
            available = template.stock or 0
        else:
            overridden_fields = set(override.overridden_fields or [])
            available = (
                override.stock or 0
                if "stock" in overridden_fields
                else template.stock or 0
            )
            override.overridden_fields = sorted(
                overridden_fields | {"stock"}
            )

        if direction < 0 and available < quantity:
            raise ValueError(
                f"Insufficient stock for {template.name}: available {available}, requested {quantity}"
            )
        override.stock = available + (direction * quantity)


def _medicine_quantities(items):
    quantities = defaultdict(int)
    for item in items:
        if not _is_medicine_item(item):
            continue
        key = (item.code or "").strip().casefold() or item.name.strip().casefold()
        quantities[key] += item.qty or 0
    return quantities


def _apply_replaced_medicine_stock(db, hospital_id, previous_items, replacement_items):
    old_quantities = _medicine_quantities(previous_items)
    new_quantities = _medicine_quantities(replacement_items)
    old_items_by_key = {
        ((item.code or "").strip().casefold() or item.name.strip().casefold()): item
        for item in previous_items if _is_medicine_item(item)
    }
    new_items_by_key = {
        ((item.code or "").strip().casefold() or item.name.strip().casefold()): item
        for item in replacement_items if _is_medicine_item(item)
    }

    for key in old_quantities.keys() | new_quantities.keys():
        delta = new_quantities.get(key, 0) - old_quantities.get(key, 0)
        if delta == 0:
            continue
        item = new_items_by_key.get(key) or old_items_by_key[key]
        _apply_medicine_stock(
            db,
            hospital_id,
            [item],
            -1 if delta > 0 else 1,
            {id(item): abs(delta)},
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

    try:
        _apply_medicine_stock(db, bill.hospital_id, payload.items, -1)
        db.add(bill)
        db.flush()

        for item in payload.items:
            db.add(OpdBillItem(
                bill_id=bill.id,
                category=item.category,
                name=item.name,
                code=item.code,
                qty=item.qty,
                amount=item.amount,
                discount=item.discount,
                remarks=item.remarks,
            ))

        db.commit()
        db.refresh(bill)
        return bill
    except Exception:
        db.rollback()
        raise


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
        previous_items = db.query(OpdBillItem).filter(
            OpdBillItem.bill_id == bill.id
        ).all()
        try:
            _apply_replaced_medicine_stock(
                db, hospital_id, previous_items, payload.items
            )
            db.query(OpdBillItem).filter(
                OpdBillItem.bill_id == bill.id
            ).delete(synchronize_session=False)

            for item in payload.items:
                db.add(OpdBillItem(
                    bill_id=bill.id,
                    category=item.category,
                    name=item.name,
                    code=item.code,
                    qty=item.qty,
                    amount=item.amount,
                    discount=item.discount,
                    remarks=item.remarks,
                ))
            db.commit()
        except Exception:
            db.rollback()
            raise
    else:
        db.commit()

    db.refresh(bill)

    bill.items = get_bill_items_by_bill(
        db,
        bill.id
    )

    return bill
