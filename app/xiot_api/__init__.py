#
from fastapi import FastAPI, APIRouter
from fastapi_amis_admin.admin import AdminApp


def setup(app: FastAPI, admin_app: AdminApp, **kwargs):
    # 导入相关模块
    from . import apis, route

    # 注册路由
    app.include_router(route.api_router, prefix='/xiot/api/v1')
    # 注册管理页面
    # admin_app.register_admin(admin.LogsAdmin)