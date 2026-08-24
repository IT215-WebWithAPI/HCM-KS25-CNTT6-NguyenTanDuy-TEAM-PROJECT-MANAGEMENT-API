from sqlalchemy.orm import Session
from app.models.user_model import UserModel
from typing import Optional
from app.dependencies.dependencies import get_current_user
from app.core.security import create_access_token, create_refresh_token
from app.core.config import settings
from app.dependencies.dependencies import credentials_exc
from fastapi import HTTPException, status
from app.schemas.user_schema import UserResponse

import jwt

SECRET_KEY = settings.SECRET_KEY
REFRESH_TOKEN_EXPIRE_MINUTES = settings.REFRESH_TOKEN_EXPIRE_MINUTES
ALGORITHM = settings.ALGORITHM


def search_user_admin(db: Session, key_name: Optional[str] = None, key_email: Optional[str] = None, key_is_active: Optional[bool] = None):
    db_filtered = db.query(UserModel)

    if key_name is not None:
        db_filtered = db_filtered.filter(UserModel.full_name.like(f"%{key_name}%"))

    if key_email is not None:
        db_filtered = db_filtered.filter(UserModel.email.like(f"%{key_email}%"))

    if key_is_active is not None:
        db_filtered = db_filtered.filter(UserModel.is_active == key_is_active)

    return db_filtered.all()


def refresh_token(token: str, db: Session)->str:

    try:
        payload_refresh_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload_refresh_token.get("sub")
        if email is None:
            raise credentials_exc 
    except jwt.ExpiredSignatureError: 
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Phiên đăng nhập hết hạn, vui lòng đăng nhập lại!",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except jwt.PyJWTError:
        raise credentials_exc
    

    user_db = db.query(UserModel).filter(UserModel.email == email).first()

    if user_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Người dùng không tồn tại trong hệ thống!"
        )

    if not user_db.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tài khoản người dùng đang tạm khóa!"
        )

    access_token = create_refresh_token(data={
        "sub": user_db.email,
        "id": user_db.id,
        "role": user_db.role
    })

    return {
        "access_token": access_token,
        "refresh_token": token,
        "id": user_db.id,
        "email": user_db.email,
        "role": user_db.role,
        "is_active": user_db.is_active,
        "created_at": user_db.created_at
    }