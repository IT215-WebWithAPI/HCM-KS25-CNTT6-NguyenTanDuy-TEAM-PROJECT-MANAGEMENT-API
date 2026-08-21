from fastapi import APIRouter

attachment_router = APIRouter(
    prefix="/api/attachment",
    tags=["Attachment"]
)