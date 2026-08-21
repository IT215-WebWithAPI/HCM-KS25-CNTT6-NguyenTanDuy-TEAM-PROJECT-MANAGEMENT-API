from sqlalchemy.orm import Session
from app.schemas.user_schema import UserCreate
from app.models.user_model import UserModel
from fastapi import HTTPException, status
from fastapi.exceptions import RequestValidationError
from app.core.security import hash_password

def is_name_val(name: str):
    for value in name:
        if value.isdigit():
            return False
    return True

def create_user(db: Session, user_input: UserCreate):
    list_error_input = {
        "title": "Danh sách các lỗi cần chú ý!",
        "example": "full_name: tên đày đủ không có ký số; email: email chưa tồn tại khi đăng ký, đúng định dạng email!; role: ['admin', 'user']."
    }
    list_user_db = db.query(UserModel).filter(UserModel.email == user_input.email).first()
    if list_user_db is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Email người dùng đã tồn tại trong hệ thống!"
        )

    role_list = ["admin", "user"]

    if user_input.role not in role_list:
        raise RequestValidationError(errors=list_error_input)

    if not ("@" in user_input.email and ".com" in user_input.email):
        raise RequestValidationError(errors=list_error_input)

    if not is_name_val(user_input.full_name):
        raise RequestValidationError(errors=list_error_input)

    hashed_password = hash_password(user_input.password)

    new_user = UserModel(
        email=user_input.email,
        hashed_password=hashed_password,
        full_name=user_input.full_name,
        is_active=None,
        role=user_input.role,
        created_at=None
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user