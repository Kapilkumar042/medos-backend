from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from app.schemas.doctor import (
    DoctorCreate
)
from app.schemas.doctor import UpdateDoctorProfileRequest
from app.services.doctor_service import (
    create_doctor,
    update_doctor_profile
)

from app.auth.dependencies import (
    get_current_user
)

from app.auth.permissions import (
    require_role
)

from app.schemas.doctor import (
    DoctorListResponse
)

from app.services.doctor_service import (
    get_doctors,
    get_doctor
)

from app.schemas.doctor import (
    DoctorProfileUpdate
)

from app.services.doctor_service import (
    update_my_profile
)

from app.services.doctor_service import (
    get_my_profile
)

from app.db.session import get_db

router = APIRouter(
    prefix="/doctors",
    tags=["Doctors"]
)


@router.post("/")
def create_doctor_api(
    payload: DoctorCreate,
    db=Depends(get_db),
    current_user=Depends(
        get_current_user
    )
):

    require_role(
        current_user,
        ["HOSPITAL_ADMIN"]
    )

    try:

        doctor = create_doctor(
            db,
            payload,
            current_user
        )

        return {
            "message":
            "Doctor Created Successfully",

            "doctor_id":
            doctor.id
        }

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.get(
    "/",
    response_model=list[
        DoctorListResponse
    ]
)
def get_doctors_api(
    db=Depends(get_db),
    current_user=Depends(
        get_current_user
    )
):

    return get_doctors(
        db,
        current_user
    )


@router.get(
    "/{doctor_id}",
    response_model=DoctorListResponse
)
def get_doctor_api(
    doctor_id: int,
    db=Depends(get_db),
    current_user=Depends(
        get_current_user
    )
):

    try:

        return get_doctor(
            db,
            doctor_id,
            current_user
        )

    except ValueError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e)
        )


@router.put("/profile")
def update_profile_api(
    payload: DoctorProfileUpdate,
    db=Depends(get_db),
    current_user=Depends(
        get_current_user
    )
):

    require_role(
        current_user,
        ["DOCTOR"]
    )

    try:

        doctor = update_my_profile(
            db,
            payload,
            current_user
        )

        return {
            "message":
            "Profile Updated Successfully",

            "doctor_id":
            doctor.id
        }

    except ValueError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e)
        )


@router.get("/profile")
def get_profile_api(
    db=Depends(get_db),
    current_user=Depends(
        get_current_user
    )
):

    require_role(
        current_user,
        ["DOCTOR"]
    )

    return get_my_profile(
        db,
        current_user
    )


@router.put("/{doctor_id}")
def update_doctor(
    doctor_id: int,
    payload: UpdateDoctorProfileRequest,
    db=Depends(get_db),
    current_user=Depends(get_current_user)
):
    return update_doctor_profile(
        db,
        doctor_id,
        payload
    )
