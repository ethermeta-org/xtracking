from http import HTTPStatus
from typing import Annotated
from fastapi import APIRouter, Body, Request, HTTPException
from fastapi.responses import JSONResponse
from sqlmodel import Session

from app import interface
from app.exception import OnesphereException
from app.xiot_api import schema
from app.xiot_api.crud import crud_create_tracking_record

router = APIRouter()


@router.post("/retraspects", status_code=HTTPStatus.CREATED, response_model=interface.XtrackingBaseResponse)
async def create_retraspects(item:  schema.RetraspectsCreate = Body(
            examples=[
                {
                    "jq_sn": "Foo",
                    "vendor_sn": "A very nice Item",
                    "system_code": "35.4",
                    "controller_code": "3.2",
                }
            ],
        ), request: Request = None
    ):
    db = request.app.state.db  # 获取默认engine
    try:
        with Session(db) as session:
            record = crud_create_tracking_record(session, item)
            return interface.XtrackingBaseResponse(data=record)
            # return JSONResponse(status_code=HTTPStatus.CREATED, content= )
    except Exception as e:
        raise OnesphereException(detail=str(e))

