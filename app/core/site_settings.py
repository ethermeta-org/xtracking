import os
from pathlib import Path
from typing import List
from loguru import logger
from fastapi_amis_admin.admin.settings import Settings as AmisSettings

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(AmisSettings):
    name: str = 'Xtracking'
    host: str = '0.0.0.0'
    port: int = 8011
    secret_key: str = ''
    amis_theme: str = 'antd'
    allow_origins: List[str] = None
    database_url_async = 'sqlite+aiosqlite:///amisadmin.db'
    # logger = logger


site_settings = Settings(_env_file=os.path.join(BASE_DIR, '.env'))
