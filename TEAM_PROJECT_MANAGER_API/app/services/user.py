from sqlalchemy.orm import Session
from app.models.user_model import UserModel
from typing import Optional

def search_user_admin(db: Session, key_name: Optional[str] = None, key_email: Optional[str] = None, key_is_active: Optional[bool] = None):
    db_filtered = db.query(UserModel)

    if key_name is not None:
        db_filtered = db_filtered.filter(UserModel.full_name.like(f"%{key_name}%"))

    if key_email is not None:
        db_filtered = db_filtered.filter(UserModel.email.like(f"%{key_email}%"))

    if key_is_active is not None:
        db_filtered = db_filtered.filter(UserModel.is_active == key_is_active)

    return db_filtered.all()