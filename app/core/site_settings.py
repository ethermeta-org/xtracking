import os
from pathlib import Path
from typing import List

from fastapi_amis_admin.admin.settings import Settings as AmisSettings
from loguru import logger

from app.utils import check_is_dev

BASE_DIR = os.getcwd()


class Settings(AmisSettings):
    site_title: str = 'Xtracking'
    version: str = '0.1.0'
    host: str = '0.0.0.0'
    debug: bool = check_is_dev()
    port: int = 8011
    secret_key: str = ''
    amis_theme: str = 'antd'
    allow_origins: List[str] = ['*']
    # logger = logger


site_settings = Settings(database_url_async='sqlite+aiosqlite:///data/database/xtracking.db?check_same_thread=False',
                         amis_theme='antd', logger=logger)

if not os.path.exists(os.path.join(BASE_DIR, 'data', 'database')):
    os.makedirs(os.path.join(BASE_DIR, 'data', 'database'), exist_ok=True)
