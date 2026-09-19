import pandas as pd


def create_catalog_item(db, model, payload, hospital_id):
    item = model(
        hospital_id=hospital_id,
        **payload.model_dump()
    )

    db.add(item)
    db.commit()
    db.refresh(item)

    return item


def list_catalog_items(db, model, hospital_id):
    return (
        db.query(model)
        .filter(model.hospital_id == hospital_id)
        .order_by(model.id.desc())
        .all()
    )


def update_catalog_item(
    db,
    model,
    item_id,
    payload,
    hospital_id
):
    item = (
        db.query(model)
        .filter(
            model.id == item_id,
            model.hospital_id == hospital_id
        )
        .first()
    )

    if not item:
        return None

    for key, value in payload.model_dump(
        exclude_unset=True
    ).items():
        setattr(item, key, value)

    db.commit()
    db.refresh(item)

    return item


def import_catalog_items(
    db,
    file,
    model,
    required_columns,
    hospital_id
):
    df = pd.read_excel(file.file)

    missing = [
        column for column in required_columns
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing columns: {', '.join(missing)}"
        )

    created = []
    skipped_rows = []

    for row_number, row in df.iterrows():
        data = {}

        for column in model.__table__.columns.keys():
            if column in ("id", "hospital_id", "created_at"):
                continue

            value = row.get(column)

            if value is None or (isinstance(value, float) and pd.isna(value)):
                value = None
            elif isinstance(value, str) and value.strip() == "":
                value = None

            if column == "expiry":
                if value is None or pd.isna(value):
                    data[column] = None
                    continue

                try:
                    parsed = pd.to_datetime(value, dayfirst=True, errors="coerce")
                    if pd.isna(parsed):
                        data[column] = None
                    else:
                        data[column] = parsed.date().isoformat()
                except Exception:
                    data[column] = None
                continue

            data[column] = value

        required_missing = [
            col for col in required_columns
            if col in data and data[col] is None
        ]

        if required_missing:
            skipped_rows.append(
                f"Row {row_number + 2}: missing required values -> {', '.join(required_missing)}"
            )
            continue

        item = model(
            hospital_id=hospital_id,
            **data
        )

        db.add(item)
        created.append(item)

    db.commit()

    if skipped_rows:
        return {
            "message": "Import completed with skipped invalid rows",
            "count": len(created),
            "skipped_rows": skipped_rows
        }

    return {
        "message": f"{len(created)} records imported successfully",
        "count": len(created)
    }