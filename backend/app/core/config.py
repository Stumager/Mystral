from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "postgresql+asyncpg://mystral:mystral@postgres:5432/mystral"
    redis_url: str = "redis://redis:6379/0"
    secret_key: str = "changeme"
    groq_api_key: str = ""
    telegram_bot_token: str = ""
    telegram_webapp_url: str = ""
    yukassa_shop_id: str = ""
    yukassa_secret_key: str = ""
    support_telegram_id: str = ""
    admin_token: str = ""
    smtp_host: str = ""
    smtp_port: int = 465
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = ""


settings = Settings()
