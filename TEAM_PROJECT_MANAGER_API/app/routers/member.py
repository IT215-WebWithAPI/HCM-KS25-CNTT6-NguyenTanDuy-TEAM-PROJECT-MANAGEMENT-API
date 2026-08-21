from fastapi import APIRouter

member_router = APIRouter(
    prefix="/api/member",
    tags=["member"]
)