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

project_router = APIRouter(
    prefix="/api/project",
    tags=["Project"]
)

@project_router.post("/projects", tags=["Project"], status_code=status.HTTP_201_CREATED, response_model=ResponseCreate)
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

