from fastapi import FastAPI, HTTPException, Query, APIRouter
from typing import Optional
from loguru import logger
from sqlalchemy import text
from app.core.adminsite import source_db

router = APIRouter()


@router.get("/search_sn_details")
async def get_sn_details(code: Optional[str] = Query(None, description="The serial number to search")):
    if not code:
        raise HTTPException(status_code=400, detail="Bad Request: No code provided")
    logger.debug(f"Start searching for serial number: {code}")

    # Connect to the database
    async with source_db() as session:
        logger.debug(f"Connected to the database")

        search_query = text("SELECT attribute, old_code, new_code, product_model FROM sn WHERE sn = :sn")
        result = session.execute(search_query, {"sn": code})
        logger.debug(f"Executed SQL query: {search_query}")
        record = result.fetchone()

    if not record:
        logger.debug(f"No serial number found: {code}")
        raise HTTPException(status_code=404, detail="No sn found")

    attributes, old_code, new_code, product_model = record
    info = attributes.split(',') if attributes else []
    default_code = new_code or old_code
    product_model = product_model or ""


    return {
        'default_code': default_code,
        'product_model': product_model,
        'info': info,
    }









































