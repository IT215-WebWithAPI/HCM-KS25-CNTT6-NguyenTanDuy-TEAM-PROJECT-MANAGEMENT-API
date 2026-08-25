from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Literal
from app.schemas.user_schema import UserInnerJoin

class ProjectMemberBase(BaseModel):
    class Config:
        from_attributes = True

class ProjectMemberCreate(ProjectMemberBase):
    project_id: int = Field(...)
    user_id: int = Field(...)

class ProjectMemberUpdate(ProjectMemberBase):
    project_id: int = Field(...)
    user_id: int = Field(...)
    role: str = Field(...)

class ProjectMemberResponse(ProjectMemberBase):
    id: int
    project_id: int
    user_id: int
    role: str
    joined_at: Optional[datetime]

class MemberInnerJoin(ProjectMemberBase):
    id: int
    project_id: int
    user_id: UserInnerJoin
    role: str
    joined_at: Optional[datetime]