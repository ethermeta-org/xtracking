import os
import sys
from functools import partial
from http import HTTPStatus

from fastapi import FastAPI, HTTPException
from loguru import logger
from sqlmodel import SQLModel
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.common_api.api import api_router as common_api_router
from app.config import settings as config_settings
from app.constants import API_V1_STR
from app.core.adminsite import site, scheduler
from app.core.site_settings import site_settings
from app.interface import XtrackingErrorWebResponse
from app.utils import get_database_url, create_engine, is_prod_env, check_is_dev
from app.xiot_api import setup
from app.xiot_api.sn import router as search_router


async def http_exception(request: Request, exc: Exception):
    msg = str(exc)
    logger.error(msg)
    url_path = request.url.path
    r = XtrackingErrorWebResponse(
        message='fail',
        error=msg,
        target=url_path
    )
    return JSONResponse(content=r.model_dump(), status_code=HTTPStatus.BAD_REQUEST)


exception_handlers = {
    HTTPException: http_exception,
}

app = FastAPI(debug=check_is_dev(), docs_url='/admin_docs', redoc_url='/admin_redoc',
              exception_handlers=exception_handlers)

if is_prod_env():
    logger.add(config_settings.logging.path, rotation=config_settings.logging.rotate,
               level=config_settings.logging.level,
               retention=getattr(config_settings.logging, 'retention', '15 days'),
               encoding='utf-8', enqueue=True)  # 文件日誌
if check_is_dev():
    logger.add(sys.stdout, format=config_settings.logging.format, level="DEBUG")


setup(app, site)

app.include_router(common_api_router, prefix=API_V1_STR)
app.include_router(search_router)


# 数据库连接
async def database_connect(app: FastAPI, database_url: str, attr: str = 'db') -> None:
    logger.info("Database Connecting!!!")
    try:
        engine = create_engine(database_url)

        setattr(app.state, attr, engine)   # 加入到状态中

    except Exception as e:
        logger.error(f"Database Connect Error: {e}")
    logger.info("Database Connection Established")


async def database_disconnect(app: FastAPI):
    logger.info("Database Disconnected")


async def add_config(app: FastAPI, setting):
    app.config = setting


async def create_admin_db():
    await site.db.async_run_sync(SQLModel.metadata.create_all, is_session=False)
    # 运行后台管理系统启动事件
    await site.router.startup()


# Mount the background management system
site.mount_app(app)


app.add_event_handler('startup', create_admin_db)
database_url = get_database_url(schema='postgresql', user=config_settings.DATABASE.USER, database=config_settings.DATABASE.NAME,
                                host=config_settings.DATABASE.HOST, port=config_settings.DATABASE.PORT,
                                password=config_settings.DATABASE.PASSWORD)
database_onconnect = partial(database_connect, app=app, database_url=database_url)
app.add_event_handler('startup', database_onconnect)
database_ondisconnect = partial(database_disconnect, app=app)
app.add_event_handler('shutdown', database_ondisconnect)
add_config_on_startup = partial(add_config, app=app, setting=config_settings)
app.add_event_handler('startup', add_config_on_startup)

# 1.配置 CORSMiddleware
from starlette.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=site_settings.allow_origins,  # 允许访问的源
    allow_credentials=True,  # 支持 cookie
    allow_methods=["*"],  # 允许使用的请求方法
    allow_headers=["*"]  # 允许携带的 Headers
)


# Start the scheduled task scheduler
scheduler.start()
