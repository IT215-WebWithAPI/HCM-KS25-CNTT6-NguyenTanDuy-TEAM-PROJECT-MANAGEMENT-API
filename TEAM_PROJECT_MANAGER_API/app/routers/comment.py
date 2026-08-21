from fastapi import APIRouter

comment_router = APIRouter(
    prefix="/api/comment",
    tags=["Comment"]
)