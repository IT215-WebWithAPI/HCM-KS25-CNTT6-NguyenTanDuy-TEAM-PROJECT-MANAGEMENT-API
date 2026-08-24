from sqlalchemy.orm import Session
from app.schemas.project_schema import ProjectCreate
from app.models.project_model import ProjectModel
from app.schemas.user_schema import UserResponse

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