from fastapi import APIRouter

task_router = APIRouter(
    prefix="/api/task",
    tags=["Task"]
)