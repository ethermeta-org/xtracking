import os
from pathlib import Path
from typing import List
from fastapi_amis_admin.admin.settings import Settings as AmisSettings

from app.utils import check_is_dev

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(AmisSettings):
    # name: str = 'Xtracking'
    host: str = '0.0.0.0'
    debug: bool = check_is_dev()
    port: int = 8011
    secret_key: str = ''
    amis_theme: str = 'antd'
    allow_origins: List[str] = ['*']
    database_url_async: str = 'sqlite+aiosqlite:///xtracking.db'
    # logger = logger


site_settings = Settings(_env_file=os.path.join(BASE_DIR, '.env'))
