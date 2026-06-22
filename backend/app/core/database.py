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
        for col, coltype in [
            ("zodiac_sign", "VARCHAR"), ("chinese_sign", "VARCHAR"),
            ("life_path", "INTEGER"), ("birth_lat", "FLOAT"),
            ("birth_lng", "FLOAT"), ("created_at", "TIMESTAMP DEFAULT NOW()"),
        ]:
            await conn.execute(text(
                f"ALTER TABLE user_partners ADD COLUMN IF NOT EXISTS {col} {coltype}"
            ))
