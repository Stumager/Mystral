from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "postgresql+asyncpg://mystral:mystral@postgres:5432/mystral"
    redis_url: str = "redis://redis:6379/0"
    secret_key: str = "changeme"
    groq_api_key: str = ""
    telegram_bot_token: str = ""
    telegram_webapp_url: str = ""


settings = Settings()
