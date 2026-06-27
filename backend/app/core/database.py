from contextlib import asynccontextmanager

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import settings

engine = create_async_engine(settings.database_url, echo=False, future=True)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_session():
    async with AsyncSessionLocal() as session:
        yield session


@asynccontextmanager
async def get_session_context():
    async with AsyncSessionLocal() as session:
        yield session


async def create_db_and_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
        await conn.execute(text(
            "ALTER TABLE user_profiles "
            "ADD COLUMN IF NOT EXISTS notifications_enabled BOOLEAN DEFAULT FALSE"
        ))
        await conn.execute(text(
            "ALTER TABLE users "
            "ADD COLUMN IF NOT EXISTS subscription_expires_at TIMESTAMP"
        ))
        await conn.execute(text(
            "ALTER TABLE user_profiles "
            "ADD COLUMN IF NOT EXISTS full_name VARCHAR"
        ))
        for col, ctype in [
            ("email_verified", "BOOLEAN DEFAULT FALSE"),
            ("verification_code", "VARCHAR(6)"),
            ("verification_code_expires_at", "TIMESTAMP"),
            ("reset_token", "VARCHAR(64)"),
            ("reset_token_expires_at", "TIMESTAMP"),
            ("pending_email", "VARCHAR"),
            ("pending_email_code", "VARCHAR(6)"),
            ("pending_email_expires_at", "TIMESTAMP"),
        ]:
            await conn.execute(text(
                f"ALTER TABLE users ADD COLUMN IF NOT EXISTS {col} {ctype}"
            ))
        await conn.execute(text(
            "ALTER TABLE user_profiles ADD COLUMN IF NOT EXISTS push_subscription TEXT"
        ))
        for col, ctype in [
            ("ref_code", "VARCHAR(10)"),
            ("referred_by", "UUID"),
            ("ref_bonus_days_given", "INTEGER DEFAULT 0"),
        ]:
            await conn.execute(text(
                f"ALTER TABLE users ADD COLUMN IF NOT EXISTS {col} {ctype}"
            ))
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS referral_log (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                referrer_id UUID NOT NULL REFERENCES users(id),
                referred_id UUID NOT NULL REFERENCES users(id),
                bonus_days INTEGER NOT NULL DEFAULT 7,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """))
        for col, coltype in [
            ("zodiac_sign", "VARCHAR"), ("chinese_sign", "VARCHAR"),
            ("life_path", "INTEGER"), ("birth_lat", "FLOAT"),
            ("birth_lng", "FLOAT"), ("created_at", "TIMESTAMP DEFAULT NOW()"),
        ]:
            await conn.execute(text(
                f"ALTER TABLE user_partners ADD COLUMN IF NOT EXISTS {col} {coltype}"
            ))
