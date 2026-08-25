from fastapi import APIRouter, Form, HTTPException, status, Depends, Request
from app.schemas.response_schemas import ResponseCreate
from sqlalchemy.orm import Session
from app.db.database import get_db
from typing import Optional
from datetime import datetime
from app.schemas.task_schema import TaskCreate, TaskResponse
import app.services.task as ser_task
from app.models.user_model import UserModel
from app.dependencies.dependencies import get_current_user
from app.services.response import create_response


task_router = APIRouter(
    prefix="/api",
    tags=["Tasks"]
)

@task_router.post("", response_model=ResponseCreate, status_code=status.HTTP_201_CREATED)
def create_task(
    req: Request,
    project_id: int = Form(..., description="Mã dự án của Task"),
    title: str = Form(..., description="Tiêu đề Task"),
    description: Optional[str] = Form(description="Mô tả của Task", default="Chưa có mô tả"),
    assignee_id: Optional[int] = Form(description="Người được giao Task (user_id)"),
    status_task: str = Form(..., description="Nhập mô tả cho Task (TODO / IN_PROGRESS / DONE)"),
    priority: str = Form(..., description="Mức độ quan trọng / Ưu tiên của Task (LOW / MEDIUM / HIGH)"),
    due_date: datetime = Form(description="Thời gian hết hạn",),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)

): 
    task_input = TaskCreate(project_id=project_id, title=title.strip(), description=description.strip(), assignee_id=assignee_id, status=status_task.strip().lower(), due_date=due_date, priority=priority.lower().strip())

    new_task = ser_task.create_task(db, task_input, current_user)

    data_response = TaskResponse.model_validate(new_task)

    return create_response(req, status.HTTP_201_CREATED, "Thêm Task thành công!", data_response, None)

@task_router.get("/project/{id}/task")
def get_tasks_in_project(
    req: Request,
    id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    list_tasks = ser_task.get_tasks(db, current_user, id)

    data_response = [TaskResponse.model_validate(val) for val in list_tasks]

    return create_response(req, status.HTTP_200_OK, "Lấy thành công danh sách tasks theo id dự án!", data_response, None)

@task_router.get("/tasks/{id}", status_code=status.HTTP_200_OK, response_model=ResponseCreate)
def get_task(
    req: Request,
    id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    task_db = ser_task.get_task_id(db, id, current_user)

    data_response = TaskResponse.model_validate(task_db)

    return create_response(req, status.HTTP_200_OK, "Lấy thành công Task theo id!", data_response, None)
