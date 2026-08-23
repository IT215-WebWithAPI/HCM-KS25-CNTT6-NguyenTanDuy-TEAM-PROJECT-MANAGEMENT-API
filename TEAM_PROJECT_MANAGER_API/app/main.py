from fastapi import FastAPI, HTTPException, Depends
from app.db.database import Base, get_db, engine
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.exception import register_exception_handler
from app.routers.auth import auth_router

import app.models.project_model
import app.models.user_model
import app.models.project_members_model
import app.models.task_model

import app.dependencies.dependencies

app = FastAPI()

Base.metadata.create_all(bind=engine)

register_exception_handler(app=app)

app.include_router(auth_router)

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected",
            "message": "Hệ thống đang hoạt động ổn định!"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }

