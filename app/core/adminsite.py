from fastapi_amis_admin import admin
from fastapi_amis_admin.admin import AdminSite
from fastapi_amis_admin.amis import PageSchema
from sqlalchemy_database import AsyncDatabase
from fastapi_scheduler import SchedulerAdmin

from app.core.site_settings import site_settings

async_db = AsyncDatabase.create(
    site_settings.database_url_async,
    echo=site_settings.debug,
    session_options={"expire_on_commit": False},
)


site = AdminSite(settings=site_settings, engine=async_db)

scheduler = SchedulerAdmin.bind(site)  # scheduler


@site.register_admin
class DocsAdmin(admin.IframeAdmin):
    # 设置页面菜单信息
    page_schema = PageSchema(label='开发接口文档(openapi)', icon='fa fa-book')

    # 设置跳转链接
    @property
    def src(self):
        return f'{self.app.site.settings.site_url}/admin_docs'


@site.register_admin
class ReDocsAdmin(admin.IframeAdmin):
    # 设置页面菜单信息
    page_schema = PageSchema(label='开发接口文档(redoc)', icon='fa fa-book')

    # 设置跳转链接
    @property
    def src(self):
        return f'{self.app.site.settings.site_url}/admin_redoc'

