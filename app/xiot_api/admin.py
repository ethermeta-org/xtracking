from fastapi_amis_admin import amis, admin

from app.xiot_api.models import SyncLog


#
class LogsAdmin(admin.ModelAdmin):
    page_schema = amis.PageSchema(label='同步日志', icon='fa fa-folder')
    router_prefix = '/logs'
    model = SyncLog
    search_fields = [SyncLog.sn, SyncLog.description]
    # ordering = [SyncLog.execute_datatime.desc()]
