from fastapi import APIRouter, status, HTTPException, Depends, Request, Form
from app.schemas.response_schemas import ResponseCreate
from sqlalchemy.orm import Session 
from app.db.database import get_db
from app.dependencies.dependencies import get_current_user
from app.models.user_model import UserModel
from app.schemas.project_member_schemas import ProjectMemberCreate, ProjectMemberResponse, MemberInnerJoin
from app.schemas.user_schema import UserInnerJoin
from app.services.response import create_response

import app.services.member as ser_member

member_router = APIRouter(
    prefix="/api",
    tags=["member"]
)

@member_router.post("/member", status_code=status.HTTP_201_CREATED, response_model=ResponseCreate)
def create_member(
    req: Request,
    project_id: int = Form(..., description="ID dự án"),
    user_id: int = Form(..., description="Thành viên"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    member_input = ProjectMemberCreate(project_id=project_id, user_id=user_id)

    new_member = ser_member.create_member(db, current_user, member_input)

    data_response = ProjectMemberResponse.model_validate(new_member)

    return create_response(req, status.HTTP_201_CREATED, "Thêm thành viên thành công!", data_response, None)

@member_router.delete("/projects/{id}/members/{user_id}", status_code=status.HTTP_200_OK, response_model=ResponseCreate)
def delete_member(req: Request, id: int, user_id: int, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    user_dele = ser_member.delete_member(db, id, user_id, current_user)

    data_response = ProjectMemberResponse.model_validate(user_dele)

    return create_response(req, status.HTTP_200_OK, "Xóa thành công thành viên!", data_response, None)


@member_router.get("/projects/{id}/members", status_code=status.HTTP_200_OK, response_model=ResponseCreate)
def get_members(
    req: Request, 
    id: int, 
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    members = ser_member.get_project_members(db, id)

    data_response = []

    for member, user in members:
        member_dict = {
            "id": member.id,
            "project_id": member.project_id,
            "role": member.role,
            "joined_at": member.joined_at,
            "user_id": user
        }
        validate_dict = MemberInnerJoin.model_validate(member_dict)
        data_response.append(validate_dict)


    return create_response(req, status.HTTP_200_OK, "Lấy danh sách thành viên thành công!", data_response, None)