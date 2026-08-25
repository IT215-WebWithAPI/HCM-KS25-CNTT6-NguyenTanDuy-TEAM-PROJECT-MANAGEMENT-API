from fastapi import APIRouter, Form, HTTPException, status, Depends, Request
from app.schemas.response_schemas import ResponseCreate
from sqlalchemy.orm import Session
from app.db.database import get_db
from typing import Optional
from datetime import datetime
from app.schemas.task_schema import TaskCreate, TaskResponse, TaskUpdate
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
    priority: str = Form(..., description="Mức độ quan trọng / Ưu tiên của Task (LOW / MEDIUM / HIGH)"),
    due_date: datetime = Form(description="Thời gian hết hạn",),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)

): 
    """CREATE TASK
    - **project_id**: Mã dự án của Task
    - **title**: Tiêu đề Task
    - **description**: Mô tả của Task
    - **assignee_id**: Người được giao Task (user_id)
    - **priority**: Mức độ quan trọng / Ưu tiên của Task (LOW / MEDIUM / HIGH)
    - **due_date**: Thời gian hết hạn
    - **note**: API này sẽ được sử dụng để tạo Task mới, chỉ có thể được truy cập bởi người dùng đã đăng nhập"""
    description = description.strip() if description else None
    
    task_input = TaskCreate(project_id=project_id, title=title.strip(), description=description, assignee_id=assignee_id, due_date=due_date, priority=priority.lower().strip())
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
    """GET TASKS IN PROJECT
    - **id**: ID dự án
    - **note**: API này sẽ được sử dụng để lấy danh sách tasks theo id dự án, chỉ có thể được truy cập bởi người dùng đã đăng nhập"""
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
    """GET TASK BY ID
    - **id**: ID Task
    - **note**: API này sẽ được sử dụng để lấy thông tin Task theo ID, chỉ có thể được truy cập bởi người dùng đã đăng nhập"""
    task_db = ser_task.get_task_id(db, id, current_user)

    data_response = TaskResponse.model_validate(task_db)

    return create_response(req, status.HTTP_200_OK, "Lấy thành công Task theo id!", data_response, None)


@task_router.patch("/tasks/{id}", status_code=status.HTTP_200_OK, response_model=ResponseCreate)
def update_task(
        req: Request,
        id: int,
        title: Optional[str] = Form(description="Tiêu đề Task"),
        description: Optional[str] = Form(description="Mô tả của Task", default="Chưa có mô tả"),
        assignee_id: Optional[int] = Form(description="Người được giao Task (*Chỉnh sửa hiệu lực khi bạn là owner)"),
        status_task: Optional[str] = Form(description="Nhập mô tả cho Task (TODO / IN_PROGRESS / DONE)"),
        priority: Optional[str] = Form(description="Mức độ ưu tiên(LOW / MEDIUM / HIGH)"),
        due_date: Optional[datetime] = Form(description="Thời gian hết hạn (*Chỉnh sửa hiệu lực khi bạn là owner) 'exp: 2000-01-01T00:00:00'",),
        db: Session = Depends(get_db),
        current_user: UserModel = Depends(get_current_user)
):
    """UPDATE TASK
    - **id**: ID Task
    - **title**: Tiêu đề Task (tùy chọn)
    - **description**: Mô tả của Task (tùy chọn)
    - **assignee_id**: Người được giao Task (tùy chọn)
    - **status_task**: Trạng thái của Task (tùy chọn)
    - **priority**: Mức độ ưu tiên (tùy chọn)
    - **due_date**: Thời gian hết hạn (tùy chọn)
    - **note**: API này sẽ được sử dụng để cập nhật thông tin Task, chỉ có thể được truy cập bởi người dùng đã đăng nhập"""
    title = title.strip() if title else None
    description = description.strip() if description else None
    status_task = status_task.strip().lower() if status_task else None
    priority = priority.strip().lower() if priority else None

    
    task_input = TaskUpdate(title=title, description=description, assignee_id=assignee_id, status=status_task, priority=priority, due_date=due_date)

    data_update = ser_task.update_task(db, current_user, id, task_input)
    data_response = TaskResponse.model_validate(data_update)

    return create_response(req, status.HTTP_200_OK, "Cập nhật Task theo id thành công!", data_response, None)

@task_router.delete("/tasks/{id}", status_code=status.HTTP_200_OK, response_model=ResponseCreate)
def delete_task(
    req: Request,
    id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """DELETE TASK
    - **id**: ID Task
    - **note**: API này sẽ được sử dụng để xóa Task theo ID, chỉ có thể được truy cập bởi người dùng đã đăng nhập"""
    task_deleted = ser_task.delete_task(db, current_user, id)

    data_response = TaskResponse.model_validate(task_deleted)

    return create_response(req, status.HTTP_200_OK, "Xóa Task theo id thành công!", data_response, None)

@task_router.get("/tasks", status_code=status.HTTP_200_OK, response_model=ResponseCreate)
def get_tasks_fillter_search(
    req: Request,
    status_task: Optional[str] = None,
    priority: Optional[str] = None,
    assignee_id: Optional[int] = None,
    search_title: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """GET TASKS WITH FILTER AND SEARCH
    - **status_task**: Trạng thái của Task (tùy chọn)
    - **priority**: Mức độ ưu tiên (tùy chọn)
    - **assignee_id**: ID người được giao Task (tùy chọn)
    - **search_title**: Tiêu đề Task cần tìm kiếm (tùy chọn)
    - **note**: API này sẽ được sử dụng để lấy danh sách Task theo bộ lọc và tìm kiếm, chỉ có thể được truy cập bởi người dùng đã đăng nhập"""
    status_task = status_task.strip().lower() if status_task else None
    priority = priority.strip().lower() if priority else None
    search_title = search_title.strip().lower() if search_title else None

    list_tasks = ser_task.get_tasks_filter_search(db, current_user, status_task=status_task, priority=priority, assignee_id=assignee_id, search_title=search_title)

    data_response = [TaskResponse.model_validate(val) for val in list_tasks]

    return create_response(req, status.HTTP_200_OK, "Lấy danh sách Task theo bộ lọc thành công!", data_response, None)

@task_router.get("/tasks", status_code=status.HTTP_200_OK, response_model=ResponseCreate)
def get_tasks_pagination(
    req: Request,
    page: int = 1,
    limit: int = 5,
    sort_by: Optional[str] = "created_at",
    sort_order: Optional[str] = "asc",
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """GET TASKS WITH PAGINATION
    - **page**: Trang hiện tại (mặc định là 1)
    - **limit**: Số lượng Task trên mỗi trang (mặc định là 5)
    - **sort_by**: Cột để sắp xếp (mặc định là created_at)
    - **sort_order**: Thứ tự sắp xếp (mặc định là asc)
    - **note**: API này sẽ được sử dụng để lấy danh sách Task theo phân trang, chỉ có thể được truy cập bởi người dùng đã đăng nhập"""
    sort_by = sort_by.strip().lower() if sort_by else "created_at"
    sort_order = sort_order.strip().lower() if sort_order else "asc"

    list_tasks = ser_task.get_tasks_pagination(db, current_user, page=page, limit=limit, sort_by=sort_by, sort_order=sort_order)

    data_response = [TaskResponse.model_validate(val) for val in list_tasks.get("tasks", [])]

    return create_response(req, status.HTTP_200_OK, "Lấy danh sách Task theo phân trang thành công!", data_response, None)