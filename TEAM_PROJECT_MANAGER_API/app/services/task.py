from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.schemas.task_schema import TaskCreate, TaskUpdate
from app.models.user_model import UserModel
from app.models.project_model import ProjectModel
from datetime import datetime
from app.models.project_members_model import ProjectMemberModel
from app.models.task_model import TaskModel
from typing import Optional

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
    list_priority = ["low", "medium", "high"]

    if task_input.priority not in list_priority:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mã priority không hợp lệ!"
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
        status="todo",
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

def update_task(db: Session, current_user: UserModel, id: int, task_input: TaskUpdate):
    task_db = db.query(TaskModel).filter(TaskModel.id == id).first()
    if task_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mã Tasks không tồn tại!"
        )

    project_id = task_db.project_id
    current_member = db.query(ProjectMemberModel).filter((ProjectMemberModel.project_id == project_id) & (ProjectMemberModel.user_id == current_user.id)).first()

    if current_member is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không phải là thành viên của dự án, không thể xem!"
        )

    update_data = task_input.model_dump(exclude_unset=True)

    list_status = ["todo", "in_progress", "done"]
    list_priority = ["low", "medium", "high"]

    if (("status" in update_data and update_data.get("status") not in list_status) or ("priority" in update_data and update_data.get("priority") not in list_priority)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mã status hoặc mã priority không hợp lệ!"
        )

    list_member = db.query(ProjectMemberModel).filter(ProjectMemberModel.project_id == task_db.project_id).all()
    list_member_id = [val.user_id for val in list_member if val]
    if "assignee_id" in update_data and update_data["assignee_id"] not in list_member_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Người được giao không phải là thành viên của dự án, không thể thêm!"
            )

    datetime_now = datetime.now()
    if "due_date" in update_data:
        if update_data["due_date"].timestamp() <= datetime_now.timestamp():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Hạn xử lý phải lớn hơn thời gian hiện tại!"
            )
    

    if "title" in update_data:
        task_db.title = update_data["title"]

    if "description" in update_data:
        task_db.description = update_data["description"]

    if "status" in update_data:
        task_db.status = update_data["status"]

    if "priority" in update_data:
        task_db.priority = update_data["priority"]

    if "due_date" in update_data and current_member.role == "owner":
        task_db.due_date = update_data["due_date"]

    if "assignee_id" in update_data and current_member.role == "owner":
        task_db.assignee_id = update_data["assignee_id"]

    db.commit()
    db.refresh(task_db)

    return task_db

def delete_task(db: Session, current_user: UserModel, id: int):
    task_db = db.query(TaskModel).filter(TaskModel.id == id).first()
    if task_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mã Tasks không tồn tại!"
        )

    project_id = task_db.project_id
    current_member = db.query(ProjectMemberModel).filter((ProjectMemberModel.project_id == project_id) & (ProjectMemberModel.user_id == current_user.id)).first()

    if current_member is None or current_member.role != "owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không phải là owner của dự án, không thể xóa!"
        )

    db.delete(task_db)
    db.commit()

    return task_db

def get_tasks_filter_search(
        db: Session,
        current_user: UserModel,
        status_task: Optional[str] = None,
        priority: Optional[str] = None,
        assignee_id: Optional[int] = None,
        search_title: Optional[str] = None,
):
    list_project_member = db.query(ProjectMemberModel).filter(ProjectMemberModel.user_id == current_user.id).all()
    list_project_id = [val.project_id for val in list_project_member if val]

    if not list_project_id:
        return []

    query = db.query(TaskModel).filter(TaskModel.project_id.in_(list_project_id))
    if status_task is not None:
        if status_task not in ["todo", "in_progress", "done"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mã status không hợp lệ!"
            )

        query = query.filter(TaskModel.status == status_task)

    if priority is not None:
        if priority not in ["low", "medium", "high"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mã priority không hợp lệ!"
            )

        query = query.filter(TaskModel.priority == priority)

    if assignee_id is not None:
        query = query.filter(TaskModel.assignee_id == assignee_id)

    if search_title is not None:
        query = query.filter(TaskModel.title.ilike(f"%{search_title}%"))

    return query.all()


def get_tasks_pagination(
    db: Session,
    current_user: UserModel,
    page: int = 1,
    limit: int = 5,
    sort_by: Optional[str] = "created_at",
    sort_order: Optional[str] = "asc"
):
    list_project_member = db.query(ProjectMemberModel).filter(ProjectMemberModel.user_id == current_user.id).all()
    list_project_id = [val.project_id for val in list_project_member if val]

    if not list_project_id:
        return [] 

    query = db.query(TaskModel).filter(TaskModel.project_id.in_(list_project_id))

    if sort_by not in ["created_at", "due_date"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mã sort_by không hợp lệ!"
        )

    if sort_order not in ["asc", "desc"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mã sort_order không hợp lệ!"
        )

    query = query.order_by(getattr(TaskModel, sort_by).asc() if sort_order == "asc" else getattr(TaskModel, sort_by).desc())

    total_tasks = query.count()
    total_pages = (total_tasks + limit - 1) // limit 

    offset = (page - 1) * limit
    tasks = query.offset(offset).limit(limit).all()

    return {
        "tasks": tasks, 
        "total_tasks": total_tasks,
        "total_pages": total_pages,
        "current_page": page
    }
