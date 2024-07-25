from fastapi_amis_admin.amis import PageSchema

from .site_settings import site_settings

from fastapi_amis_admin import admin
from fastapi_amis_admin.admin import AdminSite

site = AdminSite(site_settings)


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

