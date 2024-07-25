from fastapi_amis_admin import amis, admin

from .models import SyncLog

#
class LogsAdmin(admin.ModelAdmin):
    page_schema = amis.PageSchema(label='同步日志', icon='fa fa-folder')
    router_prefix = '/logs'
    model = SyncLog
    search_fields = [SyncLog.name]
