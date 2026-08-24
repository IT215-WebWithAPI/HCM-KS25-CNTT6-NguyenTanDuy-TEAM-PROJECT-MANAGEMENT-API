from sqlalchemy.orm import Session
from app.schemas.project_schema import ProjectCreate
from app.models.project_model import ProjectModel
from app.models.user_model import UserModel
from app.models.project_members_model import ProjectMemberModel
from app.schemas.user_schema import UserResponse
from typing import Optional
from fastapi import HTTPException, status

def create_project(db: Session, project_input: ProjectCreate, user_login: UserResponse):


    new_project = ProjectModel(
        name = project_input.name,
        description = project_input.description,
        owner_id = user_login.id
    )

    db.add(new_project)
    db.commit()
    db.refresh(new_project)

    return new_project

def get_projects(db: Session, current_user: UserModel , key_name: Optional[str] = None):
    rows = db.query(ProjectModel.id).filter(ProjectModel.owner_id == current_user.id).all()

    owner_member_project_id = []
    for row in rows:
        owner_member_project_id.append(row.id)

    rows = db.query(ProjectMemberModel.project_id).filter(ProjectMemberModel.user_id == current_user.id).all()

    for row in rows:
        owner_member_project_id.append(row.project_id)

    if not owner_member_project_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Người dùng không có dự án hay là thành viên của bất kỳ dự án nào1"
        )

    list_project_response = db.query(ProjectModel).filter(ProjectModel.id.in_(owner_member_project_id))

    if key_name is not None:
        list_project_response = list_project_response.filter(ProjectModel.name.like(f"%{key_name}%"))

    return list_project_response.all()


def get_project_id(db: Session, current_user: UserModel, id: int):
    rows = db.query(ProjectModel.id).filter((ProjectModel.owner_id == current_user.id) & (ProjectModel.id == id)).all()

    owner_member_project_id = []
    for row in rows:
        owner_member_project_id.append(row.id)

    rows = db.query(ProjectMemberModel.project_id).filter((ProjectMemberModel.user_id == current_user.id) & (ProjectMemberModel.project_id == id)).all()

    for row in rows:
        owner_member_project_id.append(row.project_id)

    if not owner_member_project_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Người dùng không có dự án hay là thành viên của bất kỳ dự án nào1"
        )

    data_response = db.query(ProjectModel).filter(ProjectModel.id.in_(owner_member_project_id))

    return data_response

    

