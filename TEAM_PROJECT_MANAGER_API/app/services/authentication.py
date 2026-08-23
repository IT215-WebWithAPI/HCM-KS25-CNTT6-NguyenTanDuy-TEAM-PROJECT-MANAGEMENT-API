from sqlalchemy.orm import Session
from app.schemas.user_schema import UserCreate, UserLogin
from app.models.user_model import UserModel
from fastapi import HTTPException, status
from fastapi.exceptions import RequestValidationError
from app.core.security import hash_password, verify_password
import re

pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"

def is_name_val(name: str):
    for value in name:
        if value.isdigit():
            return False
    return True

def create_user(db: Session, user_input: UserCreate):
    
    list_error_input = {
        "title": "Danh sách các lỗi cần chú ý!",
        "example": "full_name: tên đày đủ không có ký số; email: email đã tồn tại khi đăng ký, đúng định dạng email!; role: ['admin', 'user']."
    }
    user_db_exist = db.query(UserModel).filter(UserModel.email == user_input.email).first()
    if user_db_exist is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Email người dùng đã tồn tại trong hệ thống!"
        )

    role_list = ["admin", "user"]

    if user_input.role not in role_list:
        raise RequestValidationError(errors=list_error_input)

    if not (re.match(pattern, user_input.email)):
        raise RequestValidationError(errors=list_error_input)

    if not is_name_val(user_input.full_name):
        raise RequestValidationError(errors=list_error_input)

    hashed_password = hash_password(user_input.password)

    new_user = UserModel(
        email=user_input.email,
        hashed_password=hashed_password,
        full_name=user_input.full_name,
        is_active=user_input.is_active,
        role=user_input.role
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

def login_user(db: Session, user_input: UserLogin):
    user_db_exist = db.query(UserModel).filter(UserModel.email == user_input.email).first()

    if user_db_exist is None or not verify_password(user_input.password, user_db_exist.hashed_password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tài khoản và mật khẩu không chính xác!")

    if not user_db_exist.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tài khoản đã tạm khóa!")

    return user_db_exist

    