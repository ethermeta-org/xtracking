from fastapi import APIRouter

from app.common_api.endpoints.healthz import router as common_router

api_router = APIRouter()

api_router.include_router(common_router, tags=["common"])