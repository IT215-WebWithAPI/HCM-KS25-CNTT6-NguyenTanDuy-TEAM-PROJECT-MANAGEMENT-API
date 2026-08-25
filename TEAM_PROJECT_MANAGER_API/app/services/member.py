from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user_model import UserModel
from app.schemas.project_member_schemas import ProjectMemberCreate
from app.schemas.project_schema import ProjectResponse
from app.models.project_model import ProjectModel
from app.models.project_members_model import ProjectMemberModel

def create_member(db: Session, current_user: UserModel, member_input: ProjectMemberCreate):
    if (db.query(ProjectModel).filter((ProjectModel.owner_id == current_user.id) & (ProjectModel.id == member_input.project_id)).first()) is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền thêm mới thành viên khi không phải OWNER!"
        )

    if (db.query(UserModel).filter(UserModel.id == member_input.user_id).first()) is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User không tồn tại, Không thể thêm làm thành viên!"
        )

    if (db.query(ProjectMemberModel).filter((ProjectMemberModel.project_id == member_input.project_id) & (ProjectMemberModel.user_id == member_input.user_id)).first()) is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dự án này đã thêm user này rồi!"
        )

    new_member = ProjectMemberModel(
        role="member",
        project_id=member_input.project_id,
        user_id=member_input.user_id
    )

    db.add(new_member)
    db.commit()
    db.refresh(new_member)

    return new_member


def delete_member(db: Session, id: int, user_id: int, current_user: UserModel):
    project = db.query(ProjectModel).filter(ProjectModel.id == id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dự án không tồn tại!"
        )

    if (db.query(ProjectModel).filter((ProjectModel.owner_id == current_user.id) & (ProjectModel.id == id)).first()) is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền thực hiện thao tác này!"
        )

    user_dele = db.query(ProjectMemberModel).filter((ProjectMemberModel.project_id == id) & (ProjectMemberModel.user_id == user_id)).first()

    if user_dele is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy thành viên thuộc dự án mà bạn muốn xóa!"
        )

    if user_dele.role == "owner":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bạn không thể xóa vì chính bạn là owner!"
        )
    db.delete(user_dele)
    db.commit()
    return user_dele


def get_project_members(db: Session, project_id: int):
    project = db.query(ProjectModel).filter(ProjectModel.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dự án không tồn tại!"
        )

    results = db.query(ProjectMemberModel, UserModel).join(
        UserModel, ProjectMemberModel.user_id == UserModel.id
    ).filter(
        ProjectMemberModel.project_id == project_id
    ).all()

    return results

