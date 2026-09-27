import pandas as pd

from app.models.lab_test import LabTest
from app.services.shared_catalog_service import (
    DATA_FIELDS,
    deactivate_hospital_catalog_item,
    save_hospital_catalog_by_identifier,
    update_hospital_catalog_template,
)


def _lab_catalog_response(item):
    response = {field: getattr(item, field) for field in DATA_FIELDS}
    response.update({"id": item.id, "template_id": item.template_id, "test_name": item.name})
    return response

def _clean_excel_value(value):
    if value is None:
        return None

    if isinstance(value, str):
        value = value.strip()
        if value == "":
            return None

    if pd.isna(value):
        return None

    return value

def create_lab_test(
    db,
    payload,
    current_user
):
    data = payload.model_dump()
    if "test_name" in data:
        data["name"] = data.pop("test_name")
    if data.get("code") is not None:
        data["code"] = str(data["code"]).strip() or None

    template_id = data.pop("template_id", None)
    shared_test = save_hospital_catalog_by_identifier(
        db,
        current_user["hospital_id"],
        "lab",
        data,
        template_id=template_id,
    )
    if shared_test is not None:
        return _lab_catalog_response(shared_test)

    if "name" in data:
        data["test_name"] = data.pop("name")

    lab_test = LabTest(
        hospital_id=current_user["hospital_id"],
        **data
    )

    db.add(lab_test)
    db.commit()
    db.refresh(lab_test)

    return lab_test


def get_lab_tests(
    db,
    hospital_id
):
    return (
        db.query(LabTest)
        .filter(
            LabTest.hospital_id == hospital_id
        )
        .all()
    )


def update_lab_test(
    db,
    test_id,
    payload,
    hospital_id
):
    test = (
        db.query(LabTest)
        .filter(
            LabTest.id == test_id,
            LabTest.hospital_id == hospital_id
        )
        .first()
    )

    if not test:
        changes = payload.model_dump(exclude_unset=True)
        if "test_name" in changes:
            changes["name"] = changes.pop("test_name")
        shared_test = update_hospital_catalog_template(
            db,
            hospital_id,
            "lab",
            test_id,
            changes,
        )
        if shared_test is None:
            return None
        return _lab_catalog_response(shared_test)

    for key, value in payload.model_dump(
        exclude_unset=True
    ).items():
        if key == "code" and value is not None:
            value = str(value).strip() or None
        setattr(test, key, value)

    db.commit()
    db.refresh(test)

    return test


def import_lab_tests(
    db,
    file,
    current_user
):
    hospital_id = current_user["hospital_id"]

    df = pd.read_excel(file.file)

    required_columns = [
        "test_name",
        "price"
    ]

    missing = [
        col
        for col in required_columns
        if col not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing columns: {', '.join(missing)}"
        )

    created = []
    skipped_rows = []

    for row_number, row in df.iterrows():
        code = _clean_excel_value(row.get("code"))
        if code is not None:
            code = str(code).strip()

        test_name = _clean_excel_value(row.get("test_name"))
        category = _clean_excel_value(row.get("category"))
        price = _clean_excel_value(row.get("price"))

        if test_name is None or category is None or price is None:
            skipped_rows.append(
                f"Row {row_number + 2}: missing required values -> test_name/category/price"
            )
            continue

        test = LabTest(
            hospital_id=hospital_id,
            code=code,
            test_name=test_name,
            category=category,
            price=price,
            sample_type=_clean_excel_value(row.get("sample_type")),
            report_time=_clean_excel_value(row.get("report_time")),
            method=_clean_excel_value(row.get("method")),
            status=_clean_excel_value(row.get("status")) or "Active",
        )

        db.add(test)
        created.append(test)

    db.commit()

    if skipped_rows:
        return {
            "message": "Import completed with skipped invalid rows",
            "count": len(created),
            "skipped_rows": skipped_rows
        }

    return {
        "message": f"{len(created)} lab tests imported successfully",
        "count": len(created)
    }


def delete_lab_test(db, test_id, hospital_id):
    test = (
        db.query(LabTest)
        .filter(
            LabTest.id == test_id,
            LabTest.hospital_id == hospital_id,
        )
        .first()
    )

    if not test:
        return deactivate_hospital_catalog_item(
            db,
            hospital_id,
            "lab",
            test_id,
        )

    test.status = "Inactive"
    db.commit()
    db.refresh(test)

    return test