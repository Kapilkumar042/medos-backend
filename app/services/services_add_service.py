import pandas as pd

from app.models.lab_test import LabTest


def create_lab_test(
    db,
    payload,
    current_user
):
    lab_test = LabTest(
        hospital_id=current_user["hospital_id"],
        **payload.model_dump()
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
        return None

    for key, value in payload.model_dump(
        exclude_unset=True
    ).items():
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
        "category",
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

    for _, row in df.iterrows():

        test = LabTest(
            hospital_id=hospital_id,

            code=row.get("code"),
            test_name=row.get("test_name"),
            category=row.get("category"),
            price=row.get("price"),
            sample_type=row.get("sample_type"),
            report_time=row.get("report_time"),
            method=row.get("method"),
            status=row.get("status", "Active"),
        )

        db.add(test)
        created.append(test)

    db.commit()

    return {
        "message": f"{len(created)} lab tests imported successfully"
    }
