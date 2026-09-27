from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.db.session import get_db
from app.services.shared_catalog_service import (
    CATALOG_KINDS,
    export_hospital_catalog,
    import_global_catalog,
    import_hospital_catalog,
    list_global_catalog,
    list_hospital_catalog,
    update_hospital_catalog_item,
    update_hospital_catalog_template,
)

router = APIRouter(prefix="/api/shared-catalog", tags=["Shared Catalog"])


def _check_kind(kind: str):
    if kind not in CATALOG_KINDS:
        raise HTTPException(status_code=404, detail="Unknown catalog type")


def _check_global_admin(current_user):
    if current_user.get("role") not in {"ADMIN", "SUPER_ADMIN"}:
        raise HTTPException(status_code=403, detail="Global catalog administration required")


@router.post("/global/{kind}/import")
def import_global_catalog_api(
    kind: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    _check_kind(kind)
    _check_global_admin(current_user)
    try:
        return import_global_catalog(db, kind, file)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.get("/global/{kind}")
def get_global_catalog_api(
    kind: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    _check_kind(kind)
    _check_global_admin(current_user)
    return list_global_catalog(db, kind)


@router.get("/{kind}")
def get_hospital_catalog_api(
    kind: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    _check_kind(kind)
    return list_hospital_catalog(db, current_user["hospital_id"], kind)


@router.get("/{kind}/export")
def export_hospital_catalog_api(
    kind: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    _check_kind(kind)
    content = export_hospital_catalog(db, current_user["hospital_id"], kind)
    return StreamingResponse(
        content,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{kind}-catalog.xlsx"'},
    )


@router.post("/{kind}/import")
def import_hospital_catalog_api(
    kind: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    _check_kind(kind)
    try:
        return import_hospital_catalog(db, current_user["hospital_id"], kind, file)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.patch("/{kind}/items/{item_id}")
def update_hospital_catalog_api(
    kind: str,
    item_id: int,
    payload: dict,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    _check_kind(kind)
    item = update_hospital_catalog_item(db, current_user["hospital_id"], kind, item_id, payload)
    if item is None:
        raise HTTPException(status_code=404, detail="Hospital catalog item not found")
    return item


@router.patch("/{kind}/templates/{template_id}")
def update_hospital_catalog_template_api(
    kind: str,
    template_id: int,
    payload: dict,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    _check_kind(kind)
    item = update_hospital_catalog_template(
        db, current_user["hospital_id"], kind, template_id, payload
    )
    if item is None:
        raise HTTPException(status_code=404, detail="Shared catalog template not found")
    return item