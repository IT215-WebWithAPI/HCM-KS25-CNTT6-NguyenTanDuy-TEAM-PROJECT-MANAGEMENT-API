from fastapi import APIRouter

project_router = APIRouter(
    prefix="/api/project",
    tags=["Project"]
)