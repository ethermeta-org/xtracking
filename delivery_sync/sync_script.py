import os
from fastapi import FastAPI
from sqlalchemy import create_engine, Table, MetaData, select, update
from sqlalchemy.exc import SQLAlchemyError
from loguru import logger
from fastapi_amis_admin.admin.settings import Settings
from fastapi_amis_admin.admin.site import AdminSite
from fastapi_scheduler import SchedulerAdmin
from dynaconf import Dynaconf

settings = Dynaconf(
    settings_files=['config.toml'],
    environments=True,
    envvar_prefix="FASTAPI_APP"
)

source_dsn = settings.source_dsn
sink_dsn = settings.sink_dsn
sync_interval = settings.sync_interval
log_level = settings.log.level
log_directory = settings.log.directory


env = os.getenv("ENV", "dev")


# Initialize loguru
logger.add(f"{log_directory}/sync_script.log", rotation="1 day", level=log_level)

# Initialize FastAPI
app = FastAPI()

site = AdminSite(settings=Settings(database_url_async='sqlite+aiosqlite:///amisadmin.db'))
scheduler = SchedulerAdmin.bind(site)
site.mount_app(app)

# Database engines
source_engine = create_engine(source_dsn)
sink_engine = create_engine(sink_dsn)


def sync_data():
    try:
        with source_engine.connect() as source_conn, sink_engine.connect() as sink_conn:
            metadata = MetaData()
            source_table = Table("SNCX", metadata, autoload_with=source_engine)
            sink_table = Table("SNCX", metadata, autoload_with=sink_engine)

            # Select unsynced data
            query = select(source_table).where(source_table.c.FLAG == 0)
            result = source_conn.execute(query)
            rows = result.fetchall()

            # Insert or update data in sink database
            for row in rows:
                insert_query = sink_table.insert().values(**row._asdict())
                sink_conn.execute(insert_query)

                # Update flag in source database
                update_query = update(source_table).where(source_table.c.ID == row.ID).values(FLAG=1)
                source_conn.execute(update_query)

            logger.info("Data sync completed successfully")
    except SQLAlchemyError as e:
        logger.error(f"Error during sync: {e}")


@scheduler.scheduled_job(trigger='interval', seconds=sync_interval)
def interval_syncup():
    logger.info('interval task is run...')
    sync_data()
    logger.info('Data sync completed successfully')


@app.on_event("startup")
def on_startup():
    logger.info("Starting periodic data sync")
    scheduler.start()


if __name__ == "__main__":
    import uvicorn
    if env == "prod":
        uvicorn.run(app, host="0.0.0.0", port=8000, workers=4)
    else:
        uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
