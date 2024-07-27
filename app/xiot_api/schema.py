import datetime

from sqlmodel import Field, SQLModel


class RetraspectsCreate(SQLModel):
    jq_sn: str = Field(index=True)
    vendor_sn: str = Field(title='供应商序列号')
    system_code: str = Field(title='系统代码')
    controller_code: str = Field(title='控制器代码')


class Retraspects(RetraspectsCreate, table=True):
    __tablename__ = 'data_tracking'

    id: int | None = Field(default=None, primary_key=True)

    product_code: str = Field(index=True, default='TBD')
    product_name: str = Field(title='产品名称', default='TBD')
    delivery_time: datetime.datetime = Field(default_factory=datetime.datetime.utcnow, title='发货时间')
    customer_code: str = Field(index=True, title='客户代码')
    customer_name: str | None = Field(default=None, title='客户名称')


