from fastapi import APIRouter
from app.schemas.response_schemas import ResponseCreate
from app.schemas.user_schema import UserResponse
from app.models.user_model import UserModel
from fastapi import Request, Depends, status
from app.dependencies.dependencies import get_current_user, RoleChecker, get_db
from app.services.response import create_response
from app.services.user import search_user_admin, refresh_token
from sqlalchemy.orm import Session
from typing import Optional


user_router = APIRouter(
    prefix="/api/user",
    tags=["User"]
)

@user_router.get("/refresh-token", tags=["Token"], status_code=status.HTTP_200_OK, response_model=ResponseCreate)
def refresh_access_token(req: Request, token: str, db: Session = Depends(get_db)):
    data_response = refresh_token(token, db)

    return create_response(req, status.HTTP_200_OK, "Xác thực, cấp token thành công!", data_response, None)


@user_router.get("/me", response_model=ResponseCreate, status_code=status.HTTP_200_OK, tags=["Users"])
def get_user(req: Request, current_user: UserModel = Depends(get_current_user)):
    data = UserResponse.model_validate(current_user)
    return create_response(req, status.HTTP_200_OK, "Lấy thông tin người dùng thành công!", data, None)

@user_router.get("/users", response_model=ResponseCreate, status_code=status.HTTP_200_OK, tags=["Users"])
def get_admin(req: Request, key_name: Optional[str] = None, key_email: Optional[str] = None, key_is_active: Optional[bool] = None, db: Session = Depends(get_db), current_user: UserModel = Depends(RoleChecker(["admin"]))):

    data = search_user_admin(db, key_name, key_email, key_is_active)
    data_response = [UserResponse.model_validate(u) for u in data]
    return create_response(req, status.HTTP_200_OK, "Lọc User thành công!", data_response, None)

