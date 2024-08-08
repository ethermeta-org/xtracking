import json
import re
from http import HTTPStatus

from fastapi import APIRouter, Body, Request, Response, Query
from loguru import logger
from sqlmodel import Session

from app import interface
from app.exception import OnesphereException
from app.xiot_api import schema
from app.xiot_api.crud import crud_create_tracking_record, crud_conflict_records_existed, \
    crud_update_existed_records_vendor_sn, crud_existed_records, crud_fetch_record_via_code

router = APIRouter()


@router.get("/retraspects", status_code=HTTPStatus.OK, response_model=interface.XtrackingBaseResponse)
async def get_tracking_records(code: str = Query(openapi_examples={"normal": {
                "summary": "A normal example",
                "description": "A **normal** item works correctly.",
                "value": "1005737"
            }
}), request: Request = None):
    if not code:
        response = {
            "code": HTTPStatus.BAD_REQUEST,
            "message": "Fail",
            "data": {"msg": "Code Is Empty"},
        }
        d = interface.XtrackingBaseResponse(**response)
        return Response(status_code=HTTPStatus.BAD_REQUEST, content=d.model_dump_json(exclude_none=True))
    try:
        db = getattr(request.app.state, "db", None)  # 获取默认engine
        if not db:
            return Response(status_code=HTTPStatus.BAD_REQUEST, content=json.dumps({"msg": "DB not set"}))
        with Session(db) as session:
            existed_record, err_msg, ids = crud_fetch_record_via_code(session, code)
            if not existed_record:
                msg = f"未找到相应的记录: {code}"
                response = {
                    "code": HTTPStatus.BAD_REQUEST,
                    "message": msg,
                    "data": {
                        "msg": msg
                    },
                }
                d = interface.XtrackingBaseResponse(**response)
                return Response(status_code=HTTPStatus.BAD_REQUEST, content=d.model_dump_json(exclude_none=True))
            if err_msg:
                response = {
                    "code": HTTPStatus.CONFLICT,
                    "message": err_msg,
                    "data": {
                        "id": existed_record.id,
                        "jq_sn": existed_record.jq_sn,
                        "vendor_sn": existed_record.vendor_sn,
                        "system_code": existed_record.system_code,
                        "controller_code": existed_record.controller_code,
                    },
                    "extra": {
                        "ids": ids
                    }
                }
                d = interface.XtrackingBaseResponse(**response)
                return Response(status_code=HTTPStatus.CONFLICT, content=d.model_dump_json(exclude_none=True))
            response = {
                "code": HTTPStatus.OK,
                "message": f"Fetched records successfully, Code: {code}.",
                "data": {
                    "id": existed_record.id,
                    "jq_sn": existed_record.jq_sn,
                    "vendor_sn": existed_record.vendor_sn,
                    "system_code": existed_record.system_code,
                    "controller_code": existed_record.controller_code,
                },
            }
            d = interface.XtrackingBaseResponse(**response)
            return Response(status_code=HTTPStatus.OK, content=d.model_dump_json(exclude_none=True))
    except Exception as e:
        raise OnesphereException(detail=str(e))


@router.post("/retraspects", status_code=HTTPStatus.CREATED, response_model=interface.XtrackingBaseResponse)
async def create_retraspects(item: schema.RetraspectsCreate = Body(
    examples=[
        {
            "operator": "张三",
            "jq_sn": "1005737",
            "vendor_sn": "JQ240123034",
            "system_code": "000184-70EEEE-EZ01",
            "controller_code": "ks77h2eggmc0x9t0k36bqnsts6tb2y1268p3r4kngcn3mw4mzaxpd6y5c8qu6hws62wx6w0c8nf akzxz9ap2g37tb43x10q722ko2k0L6Iaavp/aUg+BN/xn0iqRW+ 2rHDR+b77x0ra3BSxMsQBUx1Ug3VN4]CPypeUdf2VBkjqrTZk=yk06ovxovunk4s3lwqunux1cd 7zv9kj7kztobgcm0qm58p6kg08qd927g22522c2hlrscieszhx86ismzgdd5vk1d26f4yy2kpuc",
        },
        {
            "operator": "张三",
            "jq_sn": "100573711",
            "vendor_sn": "JQ240123034",
            "system_code": "000184-70EEEE-EZ01",
            "controller_code": "ks77h2eggmc0x9t0k36bqnsts6tb2y1268p3r4kngcn3mw4mzaxpd6y5c8qu6hws62wx6w0c8nf akzxz9ap2g37tb43x10q722ko2k0L6Iaavp/aUg+BN/xn0iqRW+ 2rHDR+b77x0ra3BSxMsQBUx1Ug3VN4]CPypeUdf2VBkjqrTZk=yk06ovxovunk4s3lwqunux1cd 7zv9kj7kztobgcm0qm58p6kg08qd927g22522c2hlrscieszhx86ismzgdd5vk1d26f4yy2kpuc",
        },
        {
            "operator": "张三",
            "jq_sn": "1005737",
            "vendor_sn": "JQ24012303422",
            "system_code": "000184-70EEEE-EZ01",
            "controller_code": "ks77h2eggmc0x9t0k36bqnsts6tb2y1268p3r4kngcn3mw4mzaxpd6y5c8qu6hws62wx6w0c8nf akzxz9ap2g37tb43x10q722ko2k0L6Iaavp/aUg+BN/xn0iqRW+ 2rHDR+b77x0ra3BSxMsQBUx1Ug3VN4]CPypeUdf2VBkjqrTZk=yk06ovxovunk4s3lwqunux1cd 7zv9kj7kztobgcm0qm58p6kg08qd927g22522c2hlrscieszhx86ismzgdd5vk1d26f4yy2kpuc",
        },
    ],
), request: Request = None
):
    # 首先判断jq_sn有效性
    if not re.match(r"^\d{7}$", item.jq_sn):
        response = {
            "code": HTTPStatus.BAD_REQUEST,
            "message": "Fail",
            "data": {"msg": "JQ SN must be 7 digits."},
        }
        d = interface.XtrackingBaseResponse(**response)
        return Response(status_code=HTTPStatus.BAD_REQUEST, content=d.model_dump_json(exclude_none=True))

    if not re.match(r"^(JQ\d{9}|K\d{11})$", item.vendor_sn):
        response = {
            "code": HTTPStatus.BAD_REQUEST,
            "message": "Fail",
            "data": {
                "msg": "Vendor SN must start with 'JQ' followed by 9 digits or 'K' followed by 11 digits."
            },
        }
        d = interface.XtrackingBaseResponse(**response)
        return Response(status_code=HTTPStatus.BAD_REQUEST, content=d.model_dump_json(exclude_none=True))

    try:
        db = getattr(request.app.state, "db", None)   # 获取默认engine
        if not db:
            return Response(status_code=HTTPStatus.BAD_REQUEST, content=json.dumps({"msg": "DB not set"}))
        with Session(db) as session:
            # 三码同时重复的存在
            existed_record = crud_existed_records(session, item)
            if existed_record:
                logger.info(f'存在完全相同记录: {item.jq_sn}!!!')
                crud_update_existed_records_vendor_sn(session, existed_record, item.vendor_sn)
                response = {
                    "code": HTTPStatus.OK,
                    "message": "Update a Record Success, Tip: This record database already exists and will be overwritten.",
                    "data": {
                        "id": existed_record.id,
                        "jq_sn": existed_record.jq_sn,
                        "vendor_sn": existed_record.vendor_sn,
                        "system_code": existed_record.system_code,
                        "controller_code": existed_record.controller_code,
                    },
                }
                d = interface.XtrackingBaseResponse(**response)
                return Response(status_code=HTTPStatus.OK, content=d.model_dump_json(exclude_none=True))

            # 两码或者一码重复的情况存在
            conflict_record = crud_conflict_records_existed(session, item)
            if conflict_record:
                logger.info(f'存在conflict记录: {item.jq_sn}!!!')
                response = {
                    "code": HTTPStatus.CONFLICT,
                    "message": f"Fail, Cause: system_code or controller_code conflicted with original data in the database, "
                               f"Please check! Conflict id:{conflict_record.id}",
                    "data": {
                        "id": conflict_record.id,
                        "jq_sn": conflict_record.jq_sn,
                        "vendor_sn": conflict_record.vendor_sn,
                        "system_code": conflict_record.system_code,
                        "controller_code": conflict_record.controller_code,
                    },
                }
                d = interface.XtrackingBaseResponse(**response)
                return Response(status_code=HTTPStatus.CONFLICT, content=d.model_dump_json(exclude_none=True))

            # 正常创建记录
            record = crud_create_tracking_record(session, item)
            return interface.XtrackingBaseResponse(data=record)
    except Exception as e:
        raise OnesphereException(detail=str(e))
