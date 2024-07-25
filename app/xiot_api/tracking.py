from http import HTTPStatus
from typing import Union

from fastapi import APIRouter, Header, Response

from app.xiot_api import schema

router = APIRouter()


@router.post("/retraspects", response_model=schema.Retraspects)
async def create_retraspects(item: schema.RequestRetraspects):
    return Response(status_code=HTTPStatus.NO_CONTENT)
