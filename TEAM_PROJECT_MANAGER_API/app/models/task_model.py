from app.db.database import Base
from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey, Enum as SQLEnum, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import enum

class EnumStatusTask(str, enum.Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"

class EnumPriorityTask(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class TaskModel(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(SQLEnum(EnumStatusTask, native_enum=False), nullable=False)
    priority = Column(SQLEnum(EnumPriorityTask, native_enum=False), nullable=False)
    due_date = Column(DateTime)
    created_at = Column(DateTime, nullable=False)

    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    assignee_id = Column(Integer, ForeignKey("users.id"))

    project = relationship("ProjectModel", back_populates="task")
    assignee = relationship("UserModel", back_populates="task")
