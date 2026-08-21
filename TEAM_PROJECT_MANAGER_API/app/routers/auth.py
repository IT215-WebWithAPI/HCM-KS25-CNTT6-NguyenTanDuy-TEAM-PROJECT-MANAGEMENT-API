from fastapi import APIRouter, HTTPException, status, Depends, Request
from app.schemas.user_schema import UserCreate, UserResponse
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.response import create_response

import app.services.authentication as ser_auth

auth_router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"]
)


@auth_router.post("/register", tags=["Authentication"], status_code=status.HTTP_201_CREATED)
def create_user(req: Request, user_input:  UserCreate, db: Session = Depends(get_db)):
    new_user_created = ser_auth.create_user(db, user_input)
    user_response = UserResponse.model_validate(new_user_created)

    return create_response(req, status.HTTP_201_CREATED, "Thêm thành công User!", user_response, None)