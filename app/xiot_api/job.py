import pprint
from datetime import datetime
from typing import List

from sqlalchemy.orm import load_only
from sqlmodel import col

from app.core.adminsite import scheduler, async_db, source_db, sink_db
from loguru import logger
from sqlalchemy import insert, select, update, delete
from dateutil.relativedelta import relativedelta
from app.xiot_api.models import SyncLog, MSDelivery
from app.config import settings
from app.xiot_api.schema import Retraspects

sync_interval = int(settings.sync.sync_interval)

sync_interval = 5 if sync_interval < 5 else sync_interval  # 最低不小于5分钟


@scheduler.scheduled_job('interval', minutes=60)
async def cron_task_delete_hist_sync_log():
    logger.info(f'开始启动删除历史同步日志任务')

    async with async_db():
        delta = relativedelta(days=30)
        end_date = datetime.today() - delta
        stmt = select(SyncLog.id).where(SyncLog.execute_datatime < end_date).limit(100)
        d = await async_db.async_execute(stmt)
        r = d.all()
        ids = [d[0] for d in r]  # 变成id的列表

        del_stmt = delete(SyncLog).where(col(SyncLog.id).in_(ids))
        result = await async_db.async_execute(del_stmt)
        r = result.rowcount
        logger.info(f'删除历史同步日志任务完成。删除日志数量: {r}')


@scheduler.scheduled_job('interval', seconds=5)
# @scheduler.scheduled_job('interval', minutes=sync_interval)
async def cron_task_sync_delivery_records_mssql_to_pg():
    logger.info(f'[EMPOWER]开始同步生产物流信息')

    async with source_db():
        fetch_need_update_stmt = select(MSDelivery).where(MSDelivery.FLAG == 0).limit(100)  # 获取100条需要更新的数据
        d = await source_db.async_execute(fetch_need_update_stmt)
        r = d.all()
        records: List[MSDelivery] = [d[0] for d in r]  # 变成MSDelivery对象列表
        logger.info(f"获取到需要同步的发货信息: {len(records)}条记录")
        async with sink_db():
            for delivery_record in records:
                logger.debug(f"开始同步发货信息: {delivery_record.model_dump_json(indent=4)}")
                logger.info(f"开始同步发货信息, FNUMBER序列号: {delivery_record.FNUMBER}")


