from datetime import datetime
from typing import Optional

import pytz
import sqlmodel
from fastapi_amis_admin import amis
from fastapi_amis_admin.models import Field, TextChoices

from app.constants import ENV_DEFAULT_TIMEZONE

DEFAULT_TZ = pytz.timezone(ENV_DEFAULT_TIMEZONE)




class SyncLogState(TextChoices):
    ready = "待执行"
    doing = "进行中"
    success = "成功"
    fail = "失败"


class BaseSQLModel(sqlmodel.SQLModel):
    id: Optional[int] = Field(default=None, primary_key=True)


class SyncLog(BaseSQLModel, table=True):
    __tablename__ = 'sync_log'
    name: str = Field(
        title='名称',
        sa_column=sqlmodel.Column(sqlmodel.String(100), unique=True, index=True, nullable=False)
    )
    description: str = Field(default='', title='描述', amis_form_item=amis.Textarea())
    execute_datatime: datetime = Field(default_factory=datetime.now, title='执行时间')
    state: SyncLogState = Field(default=SyncLogState.ready, title='状态')
    duration: float = Field(default=0.0, title='执行时长')


class MSDelivery(sqlmodel.SQLModel, table=True):
    __tablename__ = 'SNCX'
    ID: Optional[int] = Field(default=None, primary_key=True)
    FSERIALID: str = Field(title='Serial ID')
    FNUMBER: str = Field(title='序列号')
    mFNUMBER: str = Field(title='物料号')
    FSN: str = Field(title='Serial Number')
    F_WISY_ZBTIME: int = Field(title='质保期月')
    FDESCRIPTION: str = Field(title='备注')
    oblFNAME: str = Field(title='单据名称')
    orglFNAME: str = Field(title='组织名称')
    FSTATE: int = Field(title='状态')
    FBILLNO: str = Field(title='单据编号')
    FBILLDATE: datetime = Field(default_factory=datetime.now, title='单据日期')
    FORDERNO: str = Field(title='订单编号')
    FINPUTDATE: datetime = Field(title='入库日期冗余')
    sulFNAME: str = Field(title='供应商名称')
    culFNAME: str = Field(title='客户名称')
    FLOT: str = Field(title='批次')
    stlFNAME: str = Field(title='仓库名称')
    FCREATEDATE: datetime = Field(title='Create Date')
    FPRODUCEDATE: datetime = Field(title='Produce Date')
    FSTARTDATE: datetime = Field(title='Start Date')
    FENDDATE: datetime = Field(title='End Date')
    FSALEDATE: datetime = Field(title='Sale Date')
    FLAG: int = Field(default=0, title='Flag')  # 0为初始值，同步完后设置为1
