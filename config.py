from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "sqlite+aiosqlite:///./app.db"
    analytics_interval_minutes: int = 60

    class Config:
        env_file = ".env"