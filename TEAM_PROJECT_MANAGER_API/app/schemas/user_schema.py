from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Literal

class UserBase(BaseModel):
    email: str = Field(...)

    class Config:
        from_attributes = True

class UserCreate(UserBase):
    password: str = Field(...)
    full_name: str = Field(...)
    role: str = "user"
    is_active: bool = True

class UserLogin(UserBase):
    password: str = Field(...)

class UserUpdate(UserBase):
    full_name: str = Field(...)
    role: str = "user"
    is_active: bool = True

class UserResponse(UserBase):
    id: int
    full_name: str
    role: str
    created_at: datetime
    is_active: bool