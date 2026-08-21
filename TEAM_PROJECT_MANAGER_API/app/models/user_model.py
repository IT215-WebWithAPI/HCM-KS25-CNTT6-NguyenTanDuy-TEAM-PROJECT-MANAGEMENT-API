from app.db.database import Base
from sqlalchemy import Column, String, Integer, BOOLEAN, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone


class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(150), nullable=False, unique=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(150), nullable=False)
    role = Column(String(20), default="user", nullable=False)
    is_active = Column(BOOLEAN, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    project = relationship("ProjectModel", back_populates="owner")
    project_member = relationship("ProjectMemberModel", back_populates="user")
    task = relationship("TaskModel", back_populates="assignee")

