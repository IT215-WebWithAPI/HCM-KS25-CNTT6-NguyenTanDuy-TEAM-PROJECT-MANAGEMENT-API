from fastapi import APIRouter, HTTPException, status, Depends, Request, Form
from app.schemas.user_schema import UserCreate, UserResponse, UserLogin
from app.schemas.response_schemas import ResponseCreate
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.response import create_response
from app.core.security import create_access_token, create_refresh_token
from app.dependencies.dependencies import get_current_user, RoleChecker
from app.models.user_model import UserModel

import app.services.authentication as ser_auth

auth_router = APIRouter(
    prefix="/api",
    tags=["Authentication"]
)


@auth_router.post("/register", tags=["Authentication"], response_model=ResponseCreate, status_code=status.HTTP_201_CREATED)
def create_user(
    req: Request, 
    email: str = Form(..., description="Email"),
    password: str = Form(..., description="Mật khẩu"),
    full_name: str = Form(..., description="Họ và tên"),
    role: str = Form("user", description="Phân quyền người dùng (admin / user)"),
    is_active: bool = Form(True, description="Trạng thái tài khoản"),
    db: Session = Depends(get_db)
):
    """REGISTER USER
    - **email**: Email của người dùng
    - **password**: Mật khẩu của người dùng
    - **full_name**: Họ và tên của người dùng(không có ký số)
    - **role**: Phân quyền người dùng (admin, user)
    - **is_active**: Trạng thái tài khoản (True: Hoạt động, False: Không hoạt động)
    - **note**: Không có yêu cầu liên quan đến tạo API update của user, nên role và is_active sẽ được chọn trong lúc đăng ký để có thể demo API hoạt động có liên quan đến role và is_active."""

    email = email.strip()
    password = password.strip()
    full_name = full_name.strip()
    role = role.strip() if role else None
    
    user_input = UserCreate(email=email, password=password, full_name=full_name, role=role, is_active=is_active)
    new_user_created = ser_auth.create_user(db, user_input)
    user_response = UserResponse.model_validate(new_user_created)

    return create_response(req, status.HTTP_201_CREATED, "Thêm thành công User!", user_response, None)

@auth_router.post("/login", tags=["Authentication"], status_code=status.HTTP_200_OK)
def login_user(
    req: Request,
    email: str = Form(..., description="Tài khoản"),
    password: str = Form(..., description="Mật khẩu"),
    db: Session = Depends(get_db)
):
    """LOGIN USER
    - **email**: Email của người dùng
    - **password**: Mật khẩu của người dùng"""
    email = email.strip()
    password = password.strip()
    
    user_input = UserLogin(email=email, password=password)
    user_input_login = ser_auth.login_user(db, user_input)

    role_name = user_input_login.role if user_input_login else None

    access_token = create_access_token(data={
        "sub": user_input_login.email,
        "id": user_input_login.id,
        "role": role_name
    })

    refresh_token = create_refresh_token(data={
        "sub": user_input_login.email,
        "id": user_input_login.id
    })

    data = {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "id": user_input_login.id,
        "email": user_input_login.email,
        "role": role_name,
        "is_active": user_input_login.is_active,
        "created_at": user_input_login.created_at
    }

    return create_response(req, status.HTTP_200_OK, "Đăng nhập thành công!", data, None)



