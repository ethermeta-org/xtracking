from fastapi import APIRouter

from .tracking import router as tracking_router

api_router = APIRouter()

api_router.include_router(tracking_router, tags=["xiot"])