from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from app.db.session import get_db

from app.schemas.user import UserCreate

from app.services.user_service import (
    create_staff_user
)

from app.auth.dependencies import (
    get_current_user
)

from app.schemas.user import (
    UserResponse
)

from app.services.user_service import (
    get_staff_users
)

from app.auth.permissions import (
    require_role
)

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.post("/")
def create_user_api(
    payload: UserCreate,
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

        user = create_staff_user(
            db,
            payload,
            current_user
        )

        return {
            "message":
            "User created successfully",

            "user_id":
            user.id
        }

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    
@router.get(
    "/",
    response_model=list[UserResponse]
)
def get_users(
    db=Depends(get_db),
    current_user=Depends(
        get_current_user
    )
):

    return get_staff_users(
        db,
        current_user
    )    