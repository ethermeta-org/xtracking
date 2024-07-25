from datetime import datetime
from typing import Optional

import pytz
import sqlmodel
from fastapi_amis_admin import amis
from fastapi_amis_admin.models import Field
from app.constants import ENV_DEFAULT_TIMEZONE

DEFAULT_TZ = pytz.timezone(ENV_DEFAULT_TIMEZONE)


#
# # Create your models here.
#
class BaseSQLModel(sqlmodel.SQLModel):
    id: Optional[int] = Field(default=None,
                              sa_column=sqlmodel.Column(sqlmodel.Integer, primary_key=True, autoincrement=True))


class SyncLog(BaseSQLModel, table=True):
    __tablename__ = 'sync_log'
    name: str = Field(
        title='名称',
        sa_column=sqlmodel.Column(sqlmodel.String(100), unique=True, index=True, nullable=False)
    )
    description: str = Field(default='', title='描述', amis_form_item=amis.Textarea())
    execute_datatime: datetime = Field(default_factory=datetime.now, title='执行时间')
    state: str = Field(default='ready', title='状态')
    duration: float = Field(default=0.0, title='执行时长')
