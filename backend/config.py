import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from backend/.env if present
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


class Config:
    """Base configuration shared by all environments."""

    SECRET_KEY = os.getenv("SECRET_KEY")
    SQLALCHEMY_TRACK_MODIFICATIONS = os.getenv("SQLALCHEMY_TRACK_MODIFICATIONS")
    DB_DRIVER = "postgresql+psycopg2"

    @classmethod
    def _build_db_uri(cls, *, user, password, host, port, name):
        return f"{cls.DB_DRIVER}://{user}:{password}@{host}:{port}/{name}"


class DevelopmentConfig(Config):
    DB_USER = os.getenv("DEV_DB_USER")
    DB_PASSWORD = os.getenv("DEV_DB_PASSWORD")
    DB_HOST = os.getenv("DEV_DB_HOST")
    DB_PORT = os.getenv("DEV_DB_PORT")
    DB_NAME = os.getenv("DEV_DB_NAME")
    CREATE_DB_IF_NOT_EXISTS = True
    SQLALCHEMY_DATABASE_URI = os.getenv("DEV_DATABASE_URL") or Config._build_db_uri(
        user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT, name=DB_NAME
    )


class TestingConfig(Config):
    pass


class ProductionConfig(Config):
    pass


CONFIG_MAP = {
    "development": DevelopmentConfig,
    "dev": DevelopmentConfig,
    "testing": TestingConfig,
    "test": TestingConfig,
    "production": ProductionConfig,
    "prod": ProductionConfig,
}


def get_config_name():
    return os.getenv("FLASK_ENV") or os.getenv("APP_ENV") or "development"


def get_config_class(env_name=None):
    env = (env_name or get_config_name()).lower()
    return CONFIG_MAP.get(env, DevelopmentConfig)
