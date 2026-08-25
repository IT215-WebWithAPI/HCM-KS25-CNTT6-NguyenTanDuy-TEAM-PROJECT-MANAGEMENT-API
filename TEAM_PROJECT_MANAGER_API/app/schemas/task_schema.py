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
    assignee_id: int = Field(...)
    priority: str
    due_date: Optional[datetime] = None

class TaskUpdate(TaskBase):
    title: Optional[str] = None
    description: Optional[str] = None 
    assignee_id: Optional[int] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[datetime] = None

class TaskResponse(TaskBase):
    id: int
    project_id: int
    title: str
    description: Optional[str] = None 
    assignee_id: Optional[int] = None
    status: str
    created_at: Optional[datetime] = Field(...)
    due_date: Optional[datetime]