from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.auth.dependencies import get_current_user
from app.db.session import get_db
from app.models.catalog import (
    Department,
    HospitalService,
    Medicine,
    RadiologyTest,
)
from app.schemas.catalog import (
    DepartmentCreate,
    DepartmentUpdate,
    HospitalServiceCreate,
    HospitalServiceUpdate,
    MedicineCreate,
    MedicineUpdate,
    RadiologyCreate,
    RadiologyUpdate,
)
from app.services.catalog_service import (
    create_catalog_item,
    list_catalog_items,
    update_catalog_item,
    import_catalog_items,
    delete_catalog_item,
)
from app.models.lab_test import LabTest

from app.schemas.lab_test import (
    CreateLabTestRequest,
    UpdateLabTestRequest
)

from app.services.lab_test_service import (
    create_lab_test,
    get_lab_tests,
    update_lab_test,
    import_lab_tests
)
from app.services.lab_test_service import delete_lab_test as delete_lab_test_service
from app.services.shared_catalog_service import (
    delete_catalog_for_hospital,
    list_hospital_catalog_with_legacy,
    update_catalog_for_hospital,
)

router = APIRouter(
    # prefix="/api/catalog",
    tags=["Catalogs"]
)


@router.post("/radiology")
def create_radiology(
    payload: RadiologyCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return create_catalog_item(
        db,
        RadiologyTest,
        payload,
        current_user["hospital_id"]
    )


@router.get("/radiology")
def list_radiology(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return list_hospital_catalog_with_legacy(
        db,
        current_user["hospital_id"],
        "radiology",
        RadiologyTest,
    )


@router.put("/radiology/{item_id}")
def update_radiology(
    item_id: int,
    payload: RadiologyUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    item = update_catalog_for_hospital(
        db,
        RadiologyTest,
        "radiology",
        item_id,
        payload,
        current_user["hospital_id"]
    )

    if not item:
        raise HTTPException(404, "Radiology test not found")

    return item


@router.post("/medicine")
def create_medicine(
    payload: MedicineCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return create_catalog_item(
        db,
        Medicine,
        payload,
        current_user["hospital_id"]
    )


@router.get("/medicine")
def list_medicines(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return list_hospital_catalog_with_legacy(
        db,
        current_user["hospital_id"],
        "medicine",
        Medicine,
    )


@router.put("/medicine/{item_id}")
def update_medicine(
    item_id: int,
    payload: MedicineUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    item = update_catalog_for_hospital(
        db,
        Medicine,
        "medicine",
        item_id,
        payload,
        current_user["hospital_id"]
    )

    if not item:
        raise HTTPException(404, "Medicine not found")

    return item


@router.post("/service")
def create_service(
    payload: HospitalServiceCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return create_catalog_item(
        db,
        HospitalService,
        payload,
        current_user["hospital_id"]
    )


@router.get("/service")
def list_services(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return list_hospital_catalog_with_legacy(
        db,
        current_user["hospital_id"],
        "service",
        HospitalService,
    )


@router.put("/service/{item_id}")
def update_service(
    item_id: int,
    payload: HospitalServiceUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    item = update_catalog_for_hospital(
        db,
        HospitalService,
        "service",
        item_id,
        payload,
        current_user["hospital_id"]
    )

    if not item:
        raise HTTPException(404, "Service not found")

    return item


@router.post("/department")
def create_department(
    payload: DepartmentCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return create_catalog_item(
        db,
        Department,
        payload,
        current_user["hospital_id"]
    )


@router.get("/department")
def list_departments(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return list_catalog_items(
        db,
        Department,
        current_user["hospital_id"]
    )


@router.put("/department/{item_id}")
def update_department(
    item_id: int,
    payload: DepartmentUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    item = update_catalog_item(
        db,
        Department,
        item_id,
        payload,
        current_user["hospital_id"]
    )

    if not item:
        raise HTTPException(404, "Department not found")

    return item


@router.post("/radiology/import")
def import_radiology(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    try:
        return import_catalog_items(
            db=db,
            file=file,
            model=RadiologyTest,
            required_columns=[
                
                "name",
                "price"
            ],
            hospital_id=current_user["hospital_id"]
        )
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


@router.post("/medicine/import")
def import_medicines(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    try:
        return import_catalog_items(
            db=db,
            file=file,
            model=Medicine,
            required_columns=[
                
                "name",
                "mrp"
            ],
            hospital_id=current_user["hospital_id"]
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Database error: {str(error)}")
    except Exception as error:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Import failed: {str(error)}")


@router.post("/service/import")
def import_services(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    try:
        return import_catalog_items(
            db=db,
            file=file,
            model=HospitalService,
            required_columns=[
                
                "name",
                "price"
            ],
            hospital_id=current_user["hospital_id"]
        )
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


@router.post("/department/import")
def import_departments(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    try:
        return import_catalog_items(
            db=db,
            file=file,
            model=Department,
            required_columns=[
                
                "name"
            ],
            hospital_id=current_user["hospital_id"]
        )
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

@router.post("/lab")
def create_lab_test_api(
    payload: CreateLabTestRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return create_lab_test(
        db,
        payload,
        current_user
    )


@router.get("/lab")
def get_lab_tests_api(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return list_hospital_catalog_with_legacy(
        db,
        current_user["hospital_id"],
        "lab",
        LabTest,
    )


@router.put("/lab/{test_id}")
def update_lab_test_api(
    test_id: int,
    payload: UpdateLabTestRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    test = update_lab_test(
        db,
        test_id,
        payload,
        current_user["hospital_id"]
    )

    if not test:
        raise HTTPException(
            status_code=404,
            detail="Lab test not found"
        )

    return test


@router.post("/lab/import")
def import_lab_tests_api(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return import_lab_tests(
        db,
        file,
        current_user
    )

@router.delete("/radiology/{item_id}")
def delete_radiology(
    item_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    item = delete_catalog_for_hospital(
        db,
        RadiologyTest,
        "radiology",
        item_id,
        current_user["hospital_id"],
    )

    if not item:
        raise HTTPException(404, "Radiology test not found")

    return {"message": "Radiology test deleted successfully", "id": item_id}


@router.delete("/lab/{item_id}")
def delete_lab_test(
    item_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    item = delete_lab_test_service(db, item_id, current_user["hospital_id"])

    if not item:
        raise HTTPException(404, "Lab test not found")

    return {"message": "Lab test deleted successfully", "id": item_id}


@router.delete("/service/{item_id}")
def delete_service(
    item_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    item = delete_catalog_for_hospital(
        db,
        HospitalService,
        "service",
        item_id,
        current_user["hospital_id"],
    )

    if not item:
        raise HTTPException(404, "Service not found")

    return {"message": "Service deleted successfully", "id": item_id}    


@router.delete("/department/{item_id}")
def delete_department(
    item_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    item = delete_catalog_item(
        db,
        Department,
        item_id,
        current_user["hospital_id"],
    )

    if not item:
        raise HTTPException(404, "Department not found")

    return {"message": "Department deleted successfully", "id": item_id}


@router.delete("/medicine/{item_id}")
def delete_medicine(
    item_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    item = delete_catalog_for_hospital(
        db,
        Medicine,
        "medicine",
        item_id,
        current_user["hospital_id"],
    )

    if not item:
        raise HTTPException(404, "Medicine not found")

    return {"message": "Medicine deleted successfully", "id": item_id}


