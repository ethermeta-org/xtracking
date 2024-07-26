import sys
import os
from functools import partial
from http import HTTPStatus

from fastapi import FastAPI,HTTPException
from loguru import logger
from sqlmodel import SQLModel
from starlette.requests import Request
from starlette.responses import JSONResponse

from core.site_settings import site_settings
from core.adminsite import site
from utils import get_database_url, create_engine, get_database, is_prod_env, check_is_dev
from config import settings as config_settings
from common_api.api import api_router as common_api_router
from .constants import API_V1_STR

from fastapi_scheduler import SchedulerAdmin

from .interface import XtrackingErrorWebResponse
from .xiot_api import setup

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

app = FastAPI(debug=check_is_dev(), docs_url='/admin_docs', redoc_url='/admin_redoc',exception_handlers=exception_handlers)

config = '/app/config.yaml'

if os.path.exists(config):
    logger.info(f'从{config}文件读取配置文件')
    config_settings.load_file(path=config)  # 重新读取配置文件
else:
    logger.error(f'{config}配置文件不存在,从默认配置文件: {os.getcwd()}/config.yaml 启动!!!')

if is_prod_env():
    logger.add(config_settings.logging.path, rotation=config_settings.logging.rotate, level=config_settings.logging.level,
               encoding='utf-8', enqueue=True)  # 文件日誌
if check_is_dev():
    logger.add(sys.stdout, format=config_settings.logging.format, level=config_settings.logging.level)


scheduler = SchedulerAdmin.bind(site)  # scheduler

setup(app, site)

app.include_router(common_api_router, prefix=API_V1_STR)


# 数据库连接
async def database_connect(app: FastAPI, database_url: str) -> None:
    logger.info("Database Connecting!!!")
    engine = create_engine(database_url)

    app.state.db = engine  # 加入到状态中
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