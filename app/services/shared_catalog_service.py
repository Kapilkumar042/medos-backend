from io import BytesIO

import pandas as pd
from sqlalchemy.orm import Session

from app.models.shared_catalog import (
    HospitalCatalogOverride,
    LabCatalogTemplate,
    MedicineCatalogTemplate,
    RadiologyCatalogTemplate,
    ServiceCatalogTemplate,
)


CATALOG_KINDS = {"lab", "radiology", "service", "medicine"}
TEMPLATE_MODELS = {
    "lab": LabCatalogTemplate,
    "radiology": RadiologyCatalogTemplate,
    "service": ServiceCatalogTemplate,
    "medicine": MedicineCatalogTemplate,
}
BASE_FIELDS = (
    "code", "name", "department", "sample_type", "price", "description",
    "category", "modality", "body_part", "report_time", "unit", "status",
)
MEDICINE_FIELDS = (
    "name", "dosage_type", "pack_size", "stock", "purchase_rate",
    "unit_price", "mrp", "expiry_date",
)
DATA_FIELDS = BASE_FIELDS + tuple(
    field for field in MEDICINE_FIELDS if field not in BASE_FIELDS
)
IMPORT_FIELDS = {
    "lab": ("code", "name", "department", "sample_type", "price", "description"),
    "radiology": ("code", "name", "department", "sample_type", "price", "description"),
    "service": ("code", "name", "category", "unit", "price", "description"),
    "medicine": MEDICINE_FIELDS,
}
HEADER_ALIASES = {
    "test_name": "name",
    "service_name": "name",
    "medicine_name": "name",
    "test_code": "code",
    "price_inr": "price",
    "price_(inr)": "price",
    "descrption": "description",
    "dosage/type": "dosage_type",
    "pack_size": "pack_size",
    "purchase_rate": "purchase_rate",
    "price/tablet/pc": "unit_price",
    "expiry_date": "expiry_date",
    "description": "description",
}


def clean_value(value):
    if value is None or pd.isna(value):
        return None
    if isinstance(value, str):
        value = value.strip()
        if not value or value == "-":
            return None
    return value


def _normalize_columns(frame):
    renamed = {}
    for column in frame.columns:
        normalized = str(column).strip().lower().replace(" ", "_")
        renamed[column] = HEADER_ALIASES.get(normalized, normalized)
    return frame.rename(columns=renamed)


def _import_values(frame, row, kind):
    values = {
        field: clean_value(row.get(field))
        for field in IMPORT_FIELDS[kind]
        if field in frame.columns
    }
    if "expiry_date" in values and values["expiry_date"] is not None:
        parsed_date = pd.to_datetime(values["expiry_date"], errors="coerce")
        values["expiry_date"] = parsed_date.date() if not pd.isna(parsed_date) else None
    return values


def _template_by_identifier(db: Session, kind: str, template_id=None, code=None, name=None):
    model = TEMPLATE_MODELS[kind]
    query = db.query(model)
    if template_id is not None:
        template = query.filter(model.id == int(template_id)).first()
        if template:
            return template
    if code:
        template = query.filter(model.code == str(code)).first()
        if template:
            return template
    if name:
        return query.filter(model.name == str(name)).first()
    return None


def import_global_catalog(db: Session, kind: str, file):
    model = TEMPLATE_MODELS[kind]
    frame = _normalize_columns(pd.read_excel(file.file))
    if "name" not in frame.columns:
        raise ValueError("Missing columns: name")

    imported = 0
    skipped = []
    for row_number, row in frame.iterrows():
        values = _import_values(frame, row, kind)
        if values.get("name") is None:
            skipped.append(f"Row {row_number + 2}: missing required value -> name")
            continue

        template = _template_by_identifier(
            db, kind, template_id=clean_value(row.get("template_id")),
            code=values.get("code"), name=values["name"],
        )
        if template is None:
            template = model(name=values["name"], **{
                field: value for field, value in values.items() if field != "name"
            })
            db.add(template)
        else:
            for field, value in values.items():
                setattr(template, field, value)
        imported += 1

    db.commit()
    return {"message": "Global catalog import completed", "count": imported, "skipped_rows": skipped}


def list_hospital_catalog(db: Session, hospital_id: int, kind: str):
    model = TEMPLATE_MODELS[kind]
    templates = (
        db.query(model)
        .filter(model.status == "Active")
        .order_by(model.id)
        .all()
    )
    overrides = {}
    for item in db.query(HospitalCatalogOverride).filter(
            HospitalCatalogOverride.hospital_id == hospital_id,
            HospitalCatalogOverride.kind == kind,
            HospitalCatalogOverride.template_id.isnot(None),
    ).all():
        overrides[item.template_id] = item
    custom_items = db.query(HospitalCatalogOverride).filter(
        HospitalCatalogOverride.hospital_id == hospital_id,
        HospitalCatalogOverride.kind == kind,
        HospitalCatalogOverride.template_id.is_(None),
    ).all()

    results = []
    for template in templates:
        override = overrides.get(template.id)
        overridden_fields = set(override.overridden_fields or []) if override else set()
        effective_status = (
            override.status if "status" in overridden_fields else template.status
        )
        if effective_status != "Active":
            continue
        item_data = {
            "id": template.id,
            "template_id": template.id,
            "hospital_item_id": override.id if override else None,
            **{
                field: getattr(override, field) if field in overridden_fields else getattr(template, field)
                for field in DATA_FIELDS
            },
        }
        if kind == "medicine":
            item_data.update({
                "strength": item_data["dosage_type"],
                "form": item_data["dosage_type"],
                "purchase_price": item_data["purchase_rate"],
                "expiry": item_data["expiry_date"],
            })
        results.append(item_data)
    results.extend(
        {"id": item.id, "template_id": None, **{field: getattr(item, field) for field in DATA_FIELDS}}
        for item in custom_items
        if item.status == "Active"
    )
    return results


def list_hospital_catalog_with_legacy(db: Session, hospital_id: int, kind: str, legacy_model):
    """Return live shared items and non-duplicate rows from the legacy hospital table."""
    shared_items = list_hospital_catalog(db, hospital_id, kind)
    if kind == "lab":
        for item in shared_items:
            item["test_name"] = item["name"]
    legacy_items = db.query(legacy_model).filter(
        legacy_model.hospital_id == hospital_id
    ).order_by(legacy_model.id.desc()).all()

    shared_keys = {
        (str(item.get("code") or "").strip().casefold(), str(item.get("name") or "").strip().casefold())
        for item in shared_items
    }
    result = list(shared_items)
    for legacy_item in legacy_items:
        if getattr(legacy_item, "status", "Active") != "Active":
            continue
        legacy_name = getattr(legacy_item, "test_name", None) or getattr(legacy_item, "name", None)
        key = (
            str(getattr(legacy_item, "code", None) or "").strip().casefold(),
            str(legacy_name or "").strip().casefold(),
        )
        if key in shared_keys:
            continue
        values = {
            column.name: getattr(legacy_item, column.name)
            for column in legacy_item.__table__.columns
            if column.name not in {"hospital_id", "created_at"}
        }
        if kind == "lab":
            values["name"] = legacy_name
        values["template_id"] = None
        result.append(values)
    return result


def list_global_catalog(db: Session, kind: str):
    model = TEMPLATE_MODELS[kind]
    return db.query(model).order_by(model.id).all()


def update_hospital_catalog_item(db: Session, hospital_id: int, kind: str, item_id: int, changes: dict):
    item = db.query(HospitalCatalogOverride).filter(
        HospitalCatalogOverride.id == item_id,
        HospitalCatalogOverride.hospital_id == hospital_id,
        HospitalCatalogOverride.kind == kind,
    ).first()
    if item is None:
        return None
    for field, value in changes.items():
        if field in DATA_FIELDS:
            setattr(item, field, value)
            item.overridden_fields = sorted(set(item.overridden_fields or []) | {field})
    db.commit()
    db.refresh(item)
    return item


def update_hospital_catalog_template(db: Session, hospital_id: int, kind: str, template_id: int, changes: dict):
    model = TEMPLATE_MODELS[kind]
    template = db.query(model).filter(
        model.id == template_id,
        model.status == "Active",
    ).first()
    if template is None:
        return None

    item = db.query(HospitalCatalogOverride).filter(
        HospitalCatalogOverride.hospital_id == hospital_id,
        HospitalCatalogOverride.kind == kind,
        HospitalCatalogOverride.template_id == template_id,
    ).first()
    if item is None:
        item = HospitalCatalogOverride(
            hospital_id=hospital_id,
            template_id=template_id,
            kind=kind,
            **{
                field: getattr(template, field)
                for field in DATA_FIELDS
            },
        )
        db.add(item)
    for field, value in changes.items():
        if field in DATA_FIELDS:
            setattr(item, field, value)
            item.overridden_fields = sorted(set(item.overridden_fields or []) | {field})
    db.commit()
    db.refresh(item)
    return item


def save_hospital_catalog_by_identifier(
    db: Session,
    hospital_id: int,
    kind: str,
    changes: dict,
    template_id=None,
):
    template = _template_by_identifier(
        db,
        kind,
        template_id=clean_value(template_id),
        code=changes.get("code"),
        name=changes.get("name"),
    )
    if template is None:
        return None
    return update_hospital_catalog_template(
        db,
        hospital_id,
        kind,
        template.id,
        changes,
    )


def deactivate_hospital_catalog_template(
    db: Session,
    hospital_id: int,
    kind: str,
    template_id: int,
):
    template = db.query(TEMPLATE_MODELS[kind]).filter(
        TEMPLATE_MODELS[kind].id == template_id,
    ).first()
    if template is None:
        return None

    override = db.query(HospitalCatalogOverride).filter(
        HospitalCatalogOverride.hospital_id == hospital_id,
        HospitalCatalogOverride.kind == kind,
        HospitalCatalogOverride.template_id == template_id,
    ).first()
    if override is None:
        override = HospitalCatalogOverride(
            hospital_id=hospital_id,
            kind=kind,
            template_id=template_id,
            name=template.name,
            code=template.code,
            status="Inactive",
            overridden_fields=["status"],
        )
        db.add(override)
    else:
        override.status = "Inactive"
        override.overridden_fields = sorted(set(override.overridden_fields or []) | {"status"})

    db.commit()
    db.refresh(override)
    return override


def deactivate_hospital_catalog_item(
    db: Session,
    hospital_id: int,
    kind: str,
    item_id: int,
):
    override = db.query(HospitalCatalogOverride).filter(
        HospitalCatalogOverride.id == item_id,
        HospitalCatalogOverride.hospital_id == hospital_id,
        HospitalCatalogOverride.kind == kind,
        HospitalCatalogOverride.template_id.isnot(None),
    ).first()
    if override is not None:
        override.status = "Inactive"
        override.overridden_fields = sorted(set(override.overridden_fields or []) | {"status"})
        db.commit()
        db.refresh(override)
        return override

    return deactivate_hospital_catalog_template(db, hospital_id, kind, item_id)


def update_catalog_for_hospital(db: Session, legacy_model, kind: str, item_id: int, payload, hospital_id: int):
    template = db.query(TEMPLATE_MODELS[kind]).filter(
        TEMPLATE_MODELS[kind].id == item_id,
        TEMPLATE_MODELS[kind].status == "Active",
    ).first()
    if template is not None:
        changes = payload.model_dump(exclude_unset=True)
        if kind == "medicine":
            changes = _medicine_changes(changes)
        return update_hospital_catalog_template(
            db, hospital_id, kind, item_id, changes
        )

    local_item = db.query(legacy_model).filter(
        legacy_model.id == item_id,
        legacy_model.hospital_id == hospital_id,
    ).first()
    if local_item is not None:
        changes = payload.model_dump(exclude_unset=True)
        for field, value in changes.items():
            if hasattr(local_item, field):
                setattr(local_item, field, value)
        db.commit()
        db.refresh(local_item)
        return local_item

    changes = payload.model_dump(exclude_unset=True)
    if kind == "medicine":
        changes = _medicine_changes(changes)
    return update_hospital_catalog_template(db, hospital_id, kind, item_id, changes)


def delete_catalog_for_hospital(db: Session, legacy_model, kind: str, item_id: int, hospital_id: int):
    template = db.query(TEMPLATE_MODELS[kind]).filter(
        TEMPLATE_MODELS[kind].id == item_id,
    ).first()
    if template is not None:
        return deactivate_hospital_catalog_template(db, hospital_id, kind, item_id)

    local_item = db.query(legacy_model).filter(
        legacy_model.id == item_id,
        legacy_model.hospital_id == hospital_id,
    ).first()
    if local_item is not None:
        if kind != "medicine" and hasattr(local_item, "status"):
            local_item.status = "Inactive"
        else:
            db.delete(local_item)
        db.commit()
        return local_item
    return deactivate_hospital_catalog_item(db, hospital_id, kind, item_id)


def _medicine_changes(changes: dict) -> dict:
    field_map = {
        "strength": "dosage_type",
        "form": "dosage_type",
        "purchase_price": "purchase_rate",
        "mrp": "mrp",
        "stock": "stock",
        "expiry": "expiry_date",
        "name": "name",
        "code": "code",
        "manufacturer": "description",
        "batch_no": "pack_size",
    }
    mapped = {}
    for source, value in changes.items():
        target = field_map.get(source, source)
        if target in DATA_FIELDS:
            mapped[target] = value
    return mapped


def import_hospital_catalog(db: Session, hospital_id: int, kind: str, file):
    frame = _normalize_columns(pd.read_excel(file.file))
    if "name" not in frame.columns:
        raise ValueError("Missing columns: name")

    imported = 0
    skipped = []
    for row_number, row in frame.iterrows():
        values = _import_values(frame, row, kind)
        if values.get("name") is None:
            skipped.append(f"Row {row_number + 2}: missing required value -> name")
            continue

        template = _template_by_identifier(
            db, kind, template_id=clean_value(row.get("template_id")),
            code=values.get("code"), name=values["name"],
        )
        if template:
            item = db.query(HospitalCatalogOverride).filter(
                HospitalCatalogOverride.hospital_id == hospital_id,
                HospitalCatalogOverride.kind == kind,
                HospitalCatalogOverride.template_id == template.id,
            ).first()
            if item is None:
                item = HospitalCatalogOverride(
                    hospital_id=hospital_id,
                    template_id=template.id,
                    kind=kind,
                )
                db.add(item)
            for field, value in values.items():
                setattr(item, field, value)
                item.overridden_fields = sorted(set(item.overridden_fields or []) | {field})
        else:
            item = db.query(HospitalCatalogOverride).filter(
                HospitalCatalogOverride.hospital_id == hospital_id,
                HospitalCatalogOverride.kind == kind,
                HospitalCatalogOverride.template_id.is_(None),
                HospitalCatalogOverride.code == values.get("code"),
                HospitalCatalogOverride.name == values["name"],
            ).first()
            if item is None:
                db.add(HospitalCatalogOverride(hospital_id=hospital_id, kind=kind, **values))
            else:
                for field, value in values.items():
                    setattr(item, field, value)
        imported += 1

    db.commit()
    return {"message": "Hospital catalog import completed", "count": imported, "skipped_rows": skipped}


def export_hospital_catalog(db: Session, hospital_id: int, kind: str):
    output = BytesIO()
    pd.DataFrame(list_hospital_catalog(db, hospital_id, kind)).to_excel(output, index=False)
    output.seek(0)
    return output