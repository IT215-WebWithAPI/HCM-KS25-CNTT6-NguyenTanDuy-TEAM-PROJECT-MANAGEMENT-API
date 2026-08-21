from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Literal

class TaskBase(BaseModel):
    class Config:
        from_attributes = True

class TaskCreate(TaskBase):
    project_id: int = Field(...)
    title: str = Field(...)
    description: str
    assignee_id: int
    status: Literal["todo", "in_progress", "done"] = Field(...)
    priority: Literal["low", "medium", "high"] = Field(...)
    due_dare: Optional[datetime] = None
    created_at: Optional[datetime] = Field(...)

class TaskUpdate(TaskBase):
    project_id: int = Field(...)
    title: str = Field(...)
    description: str
    assignee_id: int
    status: Literal["todo", "in_progress", "done"] = Field(...)
    priority: Literal["low", "medium", "high"] = Field(...)

class TaskResponse(TaskBase):
    id: int
    project_id: int
    title: str
    description: str
    assignee_id: int
    status: str