from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.schemas.task_schema import TaskCreate
from app.models.user_model import UserModel
from app.models.project_model import ProjectModel
from datetime import datetime
from app.models.project_members_model import ProjectMemberModel
from app.models.task_model import TaskModel

def create_task(
        db: Session,
        task_input: TaskCreate,
        current_user: UserModel
):

    project_db = db.query(ProjectModel).filter(ProjectModel.id == task_input.project_id).first()
    if project_db is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Không tồn tại mã dự án mà bạn vừa nhập!"
        )

    list_member = db.query(ProjectMemberModel).filter(ProjectMemberModel.project_id == task_input.project_id).all()
    list_member_id = [val.user_id for val in list_member if val]

    if current_user.id not in list_member_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không phải là thành viên của dự án, không thể thêm!"
        )
    
    if task_input.assignee_id not in list_member_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Người được giao không phải là thành viên của dự án, không thể thêm!"
        )
    
    list_status = ["todo", "in_progress", "done"]
    list_priority = ["low", "medium", "high"]

    if (task_input.status not in list_status) or (task_input.priority not in list_priority):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mã status hoặc mã priority không hợp lệ!"
        )
    
    datetime_now = datetime.now()
    if task_input.due_date.timestamp() <= datetime_now.timestamp():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Hạn xử lý không phù hợp, phải lớn hơn hơn thời gian hiện tại!"
        )

    new_task = TaskModel(
        title=task_input.title,
        description=task_input.description,
        status=task_input.status,
        priority=task_input.priority,
        due_date=task_input.due_date,
        created_at=None,
        project_id=task_input.project_id,
        assignee_id=task_input.assignee_id
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return new_task

def get_tasks(db: Session, current_user: UserModel, id: int):
    if db.query(ProjectModel).filter(ProjectModel.id == id).first() is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tồn tại mã dự án này!"
        )

    if db.query(ProjectMemberModel).filter((ProjectMemberModel.user_id == current_user.id) & (ProjectMemberModel.project_id == id)).first() is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền truy cập thông tin của dự án khi bạn không phải là thành viên!"
        )

    list_tasks = db.query(TaskModel).filter(TaskModel.project_id == id).all()

    return list_tasks


def get_task_id(db: Session, id: int, current_user: UserModel):
    task_db = db.query(TaskModel).filter(TaskModel.id == id).first()

    if task_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mã Tasks không tồn tại!"
        )

    if db.query(ProjectMemberModel).filter((ProjectMemberModel.user_id == current_user.id) & (ProjectMemberModel.project_id == task_db.project_id)).first() is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không phải là thành viên của dự án, không thể xem!"
        )

    return task_db