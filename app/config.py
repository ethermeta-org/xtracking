import os

from dynaconf import Dynaconf
from loguru import logger

settings = Dynaconf(
    envvar_prefix="ENV_XT",
    settings_file="config.yaml",
    environments=False,
    load_dotenv=True,
    # env_switcher="ENV_RUNTIME_ENV",
)

config = os.getenv('ENV_CONFIG_FILE', '/opt/xtrack/config.yaml')

if os.path.exists(config):
    logger.info(f'从{config}文件读取配置文件')
    settings.load_file(path=config)  # 重新读取配置文件
else:
    logger.error(f'{config}配置文件不存在,从默认配置文件: {os.getcwd()}/config.yaml 启动!!!')