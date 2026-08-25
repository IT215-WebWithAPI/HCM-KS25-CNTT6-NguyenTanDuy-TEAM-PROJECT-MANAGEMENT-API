from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class ProjectBase(BaseModel):
    name: Optional[str] = Field(..., max_length=50)

    class Config:
        from_attributes = True

class ProjectCreate(ProjectBase):
    description: Optional[str] = None
    owner_id: int = Field(...)

class ProjectUpdate(ProjectBase):
    description: str

class ProjectResponse(ProjectBase):
    id: int
    name: str
    description: Optional[str]
    owner_id: int
    created_at: Optional[datetime]
