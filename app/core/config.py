from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    ENVIRONMENT: str = "development"
    ANALYTICS_CRON_SCHEDULE: str = "0 * * * *"
    ANALYTICS_VERSION: str = "1" #or "2"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings(DATABASE_URL = "sqlite:///./test.db")

DATABASE_URL = settings.DATABASE_URL
ENVIRONMENT = settings.ENVIRONMENT
ANALYTICS_CRON_SCHEDULE = settings.ANALYTICS_CRON_SCHEDULE
ANALYTICS_VERSION = settings.ANALYTICS_VERSION
