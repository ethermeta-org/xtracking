#
from fastapi import FastAPI
from fastapi_amis_admin.admin import AdminApp
from . import job #加载周期执行任务

def setup(app: FastAPI, admin_app: AdminApp, **kwargs):
    # 导入相关模块
    from . import admin, apis, route

    # 注册路由
    app.include_router(route.api_router, prefix='/xiot/api/v1')
    # 注册管理页面
    admin_app.register_admin(admin.LogsAdmin)