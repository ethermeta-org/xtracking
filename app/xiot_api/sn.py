from http import HTTPStatus
from typing import Optional, List, Any

from fastapi import HTTPException, Query, APIRouter, Response
from loguru import logger
from sqlalchemy import text
from starlette.responses import JSONResponse
from pydantic import BaseModel

from app.core.adminsite import search_sn_db

router = APIRouter()


class Item(BaseModel):
    default_code: str = ""
    product_model: str = ""
    info: List[Any] = ""


@router.get("/search_sn_details", status_code=HTTPStatus.OK, response_model=Item)
async def get_sn_details(code: Optional[str] = Query(default='', description="The serial number to search")):
    if not code:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Bad Request: No code provided")
    logger.debug(f"Start searching for serial number: {code}")

    # Connect to the database
    async with search_sn_db() as session:
        search_query = text("SELECT attribute, old_code, new_code, product_model FROM sn WHERE sn = :sn")
        result = session.execute(search_query, {"sn": code})
        logger.debug(f"Executed SQL query: {search_query}")
        record = result.fetchone()

    if not record:
        logger.debug(f"No serial number found: {code}")
        return JSONResponse(status_code=HTTPStatus.BAD_REQUEST, content={"result": "No serial number found",
                                                                         "errcode": HTTPStatus.NOT_FOUND})

    attributes, old_code, new_code, product_model = record
    if not old_code:
        old_code = ""
    info = attributes.split(',') if attributes else []
    default_code: str = new_code or old_code
    product_model = product_model or ""

    response = {
        'default_code': default_code.rstrip(),
        'product_model': product_model.rstrip(),
        'info': info,
    }
    d = Item(**response)
    return Response(status_code=HTTPStatus.OK, content=d.model_dump_json())
