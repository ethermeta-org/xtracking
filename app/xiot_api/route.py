from fastapi import APIRouter

from app.xiot_api.tracking import router as tracking_router

api_router = APIRouter()

api_router.include_router(tracking_router, tags=["xiot"])