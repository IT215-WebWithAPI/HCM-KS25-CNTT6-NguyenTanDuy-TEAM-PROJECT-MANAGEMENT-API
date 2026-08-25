from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class TaskBase(BaseModel):
    class Config:
        from_attributes = True

class TaskCreate(TaskBase):
    project_id: int = Field(...)
    title: str = Field(...)
    description: Optional[str]
    assignee_id: Optional[int]
    priority: str = Field(...)
    due_date: Optional[datetime] = None

class TaskUpdate(TaskBase):
    title: str = Field(...)
    description: str
    assignee_id: int
    status: str = Field(...)
    priority: str = Field(...)
    due_date: Optional[datetime]

class TaskResponse(TaskBase):
    id: int
    project_id: int
    title: str
    description: str
    assignee_id: int
    status: str
    created_at: Optional[datetime] = Field(...)
    due_date: Optional[datetime]