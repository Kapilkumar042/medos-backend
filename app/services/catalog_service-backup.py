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
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing columns: {', '.join(missing)}"
        )

    created = []

    for _, row in df.iterrows():
        data = {}

    for column in model.__table__.columns.keys():
        if column in ("id", "hospital_id", "created_at"):
            continue

        value = row.get(column)

        if pd.isna(value) or str(value).strip() == "":
            data[column] = None
            continue

        if column == "expiry":
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

        item = model(
        hospital_id=hospital_id,
        **data
        )

        db.add(item)
        created.append(item)

    db.commit()

    return {
        "message": f"{len(created)} records imported successfully",
        "count": len(created)
    }
