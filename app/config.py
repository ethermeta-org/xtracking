
from dynaconf import Dynaconf

settings = Dynaconf(
    envvar_prefix="ENV_XT",
    settings_file="config.yaml",
    environments=False,
    load_dotenv=True,
    # env_switcher="ENV_RUNTIME_ENV",
)