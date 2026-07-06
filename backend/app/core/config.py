from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "postgresql+asyncpg://mystral:mystral@postgres:5432/mystral"
    redis_url: str = "redis://redis:6379/0"
    secret_key: str = "changeme"
    groq_api_key: str = ""
    openrouter_api_key: str = ""
    telegram_bot_token: str = ""
    telegram_webapp_url: str = ""
    frontend_url: str = "https://mystral.space"
    yukassa_shop_id: str = ""
    yukassa_secret_key: str = ""
    support_telegram_id: str = ""
    admin_token: str = ""
    resend_api_key: str = ""
    smtp_from: str = "noreply@mail.mystral.space"
    vapid_private_key: str = ""
    vapid_public_key: str = ""
    vapid_claims_email: str = "mailto:noreply@mail.mystral.space"
    seo_warm_langs: str = "ru"


settings = Settings()
