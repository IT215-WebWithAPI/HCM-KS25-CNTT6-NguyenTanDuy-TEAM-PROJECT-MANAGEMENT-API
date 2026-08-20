from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    email: str = Field(...)

    class Config:
        from_attributes = True

class UserCreate(UserBase):
    original_password: str = Field(...)
    full_name: str = Field(...)
    role: str = "user"
    is_active: bool = True
    created_at: Optional[datetime] = Field(...)

class UserUpdate(UserBase):
    full_name: str = Field(...)
    role: str = "user"
    is_active: bool = True

class UserResponse(UserBase):
    id: int
    full_name: str
    role: str
    is_active: bool