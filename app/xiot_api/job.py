import os
import pprint
from datetime import datetime
from typing import List

from sqlalchemy.orm import load_only
from sqlmodel import col

from app.core.adminsite import scheduler, async_db, source_db, sink_db
from loguru import logger
from sqlalchemy import insert, select, update, delete, desc
from dateutil.relativedelta import relativedelta
from app.xiot_api.models import SyncLog, MSDelivery, SyncLogState
from app.config import settings
from app.xiot_api.schema import Retraspects

sync_interval = int(settings.sync.sync_interval)

sync_interval = 5 if sync_interval < 5 else sync_interval  # 最低不小于5分钟

ENV_SYNC_DELIVERY_RECORD_LIMIT = int(os.getenv('ENV_SYNC_DELIVERY_RECORD_LIMIT', '100'))


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


# @scheduler.scheduled_job('interval', seconds=5)
@scheduler.scheduled_job('interval', minutes=sync_interval)
async def cron_task_sync_delivery_records_mssql_to_pg():
    logger.info(f'[EMPOWER]开始同步生产物流信息')

    async with source_db():
        fetch_need_update_stmt = select(MSDelivery).where(MSDelivery.FLAG == 0).order_by(
            desc(MSDelivery.FSALEDATE)).limit(ENV_SYNC_DELIVERY_RECORD_LIMIT)  # 获取100条需要更新的数据
        d = await source_db.async_execute(fetch_need_update_stmt)
        r = d.all()
        records: List[MSDelivery] = [d[0] for d in r]  # 变成MSDelivery对象列表
        logger.info(f"获取到需要同步的发货信息: {len(records)}条记录")
        async with async_db():
            async with sink_db():
                for delivery_record in records:
                    logger.debug(f"开始同步发货信息: {delivery_record.model_dump_json(indent=4)}")
                    logger.info(f"开始同步发货信息, FNUMBER序列号: {delivery_record.FNUMBER}")

                    dn = delivery_record.FNUMBER
                    start_time = datetime.now()
                    log = SyncLog(
                        sn=dn,
                        description=f'同步发货信息,该记录id为{delivery_record.ID}。',
                        execute_datatime=start_time,
                        state=SyncLogState.ready,  # 待执行
                    )

                    # 1. 检查序列号是否为空, 若为空则失败
                    if not dn:
                        log.state = SyncLogState.fail
                        log.description += f" 序列号为空"
                        log.duration = (datetime.now() - start_time).total_seconds()
                        insert_stmt = insert(SyncLog).values(log.model_dump())
                        await async_db.async_execute(insert_stmt)
                        continue

                    match_sn_stmt = select(Retraspects).where(Retraspects.jq_sn == dn).limit(1)
                    d = await sink_db.async_execute(match_sn_stmt)
                    r: Retraspects = d.one_or_none()

                    # 2. 检查是否已经存在对应的记录, 若存在则更新, 不存在则失败
                    if not r:
                        logger.error(f"没有找到对应的记录, 发货FNUMBER序列号: {dn}")

                        log.state = SyncLogState.fail
                        log.description = f"没有找到该序列号对应的记录: {dn}"
                        log.duration = (datetime.now() - start_time).total_seconds()
                        logger.debug(f"log updated to {log}")
                        insert_stmt = insert(SyncLog).values(log.model_dump())
                        await async_db.async_execute(insert_stmt)
                        continue

                    # 3. 更新对应的记录
                    logger.debug(f"找到已存在的对应记录: {r}")
                    log.state = SyncLogState.doing
                    v = {
                        "customer_name": delivery_record.culFNAME or "",
                        "delivery_time": delivery_record.FSALEDATE or "",  # 出库日期就是销售日期
                        "customer_code": delivery_record.cuFNUMBER or "",
                        "product_code": delivery_record.mFNUMBER or "",
                        "product_name": delivery_record.mlFNAME or ""
                    }
                    logger.debug(f"cron_task_sync_delivery_records_mssql_to_pg, 更新数据内容,: {pprint.pformat(v)}")
                    update_stmt = update(Retraspects).where(Retraspects.jq_sn == delivery_record.FNUMBER).values(
                        **v)  # 通过主键快速定位优化
                    await sink_db.async_execute(update_stmt)

                    log.state = SyncLogState.success
                    logger.info(f"更新发货FNUMBER序列号: {dn}完成")

                    update_flag_stmt = update(MSDelivery).where(MSDelivery.ID == delivery_record.ID).values(FLAG=1)
                    await source_db.async_execute(update_flag_stmt)
                    logger.info("更新source flag标记完成")

                    log.duration = (datetime.now() - start_time).total_seconds()
                    insert_stmt = insert(SyncLog).values(log.model_dump())
                    await async_db.async_execute(insert_stmt)
                    logger.info(f"记录同步日志完成,FNUMBER序列号: {delivery_record.FNUMBER}")

            logger.info("同步完成")
