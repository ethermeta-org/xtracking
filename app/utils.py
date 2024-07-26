import os

import databases
from sqlalchemy.engine import Engine
from sqlmodel import create_engine as sqlmodel_create_engine

engine = None
SessionLocal = None

ENV_RUNTIME_ENV = os.environ.get('ENV_RUNTIME_ENV', 'dev')

def is_prod_env():
    T = ['prod', 'production']
    return ENV_RUNTIME_ENV in T


def check_is_dev() -> bool:
    return ENV_RUNTIME_ENV in ['dev', 'DEV', 'development']

def get_database(database_url: str) -> databases.Database:
    database = databases.Database(database_url, min_size=5, max_size=25)
    return database


def get_database_url(schema: str, user: str, database: str, host: str, port: int, password: str) -> str:
    # SQLAlchemy specific code, as with any other app
    DATABASE_URL = f"{schema}://{user}:{password}@{host}:{port}/{database}"
    return DATABASE_URL


def create_engine(database_url: str) -> Engine:
    pool_params = {
        "pool_size": 20,
        "max_overflow": 30,
        "pool_timeout": 30,
        "pool_recycle": 1800,  # 15分钟
        "pool_pre_ping": True
    }
    engine = sqlmodel_create_engine(database_url, **pool_params, echo=True)

    return engine
