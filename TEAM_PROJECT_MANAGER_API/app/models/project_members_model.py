from app.db.database import Base
from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey, Enum as SQLEnum, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import enum

class EnumRoleProjectMember(str, enum.Enum):
    OWNER = "owner"
    MEMBER = "member"

class ProjectMemberModel(Base):
    __tablename__ = "project_members"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    role = Column(SQLEnum(EnumRoleProjectMember, native_enum=False))
    joined_at = Column(DateTime, nullable=False)

    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    project = relationship("ProjectModel", back_populates="project_member")
    user = relationship("UserModel", back_populates="project_member")

    __table_args__ = (
        UniqueConstraint("user_id", "project_id", name="unique_user_project_id"),  # <-- Thêm dấu phẩy ở đây
    )