from fastapi import APIRouter, Depends, Form, HTTPException, status
from fastapi import Request
from sqlalchemy.orm import Session
from app.dependencies.dependencies import RoleChecker, get_current_user
from app.schemas.project_schema import ProjectCreate, ProjectResponse
from app.schemas.response_schemas import ResponseCreate
from app.models.user_model import UserModel
from app.dependencies.dependencies import get_current_user
import app.services.project as ser_project
from app.services.response import create_response
from app.db.database import get_db
from typing import Optional

project_router = APIRouter(
    prefix="/api/project",
    tags=["Project"]
)

@project_router.post("/projects", tags=["Projects"], status_code=status.HTTP_201_CREATED, response_model=ResponseCreate)
def create_project(
    req: Request,
    name_project: str = Form(..., description="Tên dự án"),
    description: str = Form(description="Mô tả dự án"),
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    project_input = ProjectCreate(name=name_project, description=description, owner_id=current_user.id)

    new_project = ser_project.create_project(db, project_input, current_user)

    data_response = ProjectResponse.model_validate(new_project)

    return create_response(req, status.HTTP_201_CREATED, "Thêm dự án thành công!", data_response, None)

@project_router.get("/projects/", tags=["Projects"], response_model=ResponseCreate, status_code=status.HTTP_200_OK)
def get_projects(
    req: Request,
    key_name: Optional[str] = None,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    data_filtered = ser_project.get_projects(db, current_user, key_name)

    data_response = []
    for value in data_filtered:
        data_response.append(ProjectResponse.model_validate(value))

    return create_response(req, 200, "Lấy danh sách dự án thành công!", data_response, None)