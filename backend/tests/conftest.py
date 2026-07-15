"""Shared fixtures. Env + Redis are patched BEFORE app modules are imported."""
import os
import sys
import tempfile
from pathlib import Path

# --- environment must be set before app.core.config is imported ---
_TEST_DB = Path(tempfile.gettempdir()) / "mystral_test.db"
os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{_TEST_DB.as_posix()}"
os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["ADMIN_TOKEN"] = "test-admin-token"
os.environ["GROQ_API_KEY"] = ""
os.environ["RESEND_API_KEY"] = ""
os.environ["TELEGRAM_BOT_TOKEN"] = ""
os.environ["YUKASSA_SHOP_ID"] = "test-shop-id"
os.environ["YUKASSA_SECRET_KEY"] = "test-secret-key"

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# --- fake Redis for everything (module-level clients included) ---
import fakeredis
import fakeredis.aioredis
import redis.asyncio as _aioredis

_fake_server = fakeredis.FakeServer()


def _fake_from_url(*args, **kwargs):
    decode = kwargs.get("decode_responses", False)
    return fakeredis.aioredis.FakeRedis(server=_fake_server, decode_responses=decode)


_aioredis.from_url = _fake_from_url
_aioredis.Redis.from_url = classmethod(lambda cls, *a, **k: _fake_from_url(*a, **k))

# --- kerykeion needs a C extension (pyswisseph) that has no Windows wheel;
# tests never assert astro math, they only need the import to succeed.
# The real library is installed in the Docker image. ---
try:
    import kerykeion  # noqa: F401
except ImportError:
    import types

    _stub = types.ModuleType("kerykeion")

    class _StubSubject:  # pragma: no cover — never actually used in tests
        def __init__(self, *a, **k):
            raise RuntimeError("kerykeion stub: astro math not available in local tests")

    _stub.AstrologicalSubject = _StubSubject
    _stub.KerykeionChartSVG = _StubSubject
    sys.modules["kerykeion"] = _stub

# --- now it is safe to import the app ---
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event
from sqlmodel import SQLModel

import app.core.redis as app_redis
from app.core.database import engine, AsyncSessionLocal, get_session
from app.core.security import create_jwt
from app.main import app
from app.models.user import AuthProvider, User, UserProfile
from app.core.security import hash_password

app_redis.redis_client = _fake_from_url(decode_responses=True)

# The shared file-based test DB (see _TEST_DB above) gets hit by hundreds of
# parametrized requests plus a DROP/CREATE-TABLE cycle before every single
# test (_fresh_state below). With SQLite's default busy_timeout of 0, any
# connection that finds the file locked — including transient locks left by
# a connection that just committed, especially under Windows filesystem
# latency — fails immediately with "database is locked" instead of
# retrying. WAL mode lets readers and a writer coexist, and busy_timeout
# makes writers retry for up to 30s instead of failing instantly.
@event.listens_for(engine.sync_engine, "connect")
def _set_sqlite_pragmas(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA busy_timeout=30000")
    cursor.close()


@pytest_asyncio.fixture(autouse=True)
async def _fresh_state():
    """Fresh tables + empty Redis for every test."""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)
    r = _fake_from_url()
    await r.flushall()
    yield


@pytest_asyncio.fixture
async def db_session():
    async with AsyncSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def client():
    async def _override_session():
        async with AsyncSessionLocal() as session:
            yield session

    app.dependency_overrides[get_session] = _override_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


async def make_user(
    email: str | None = "user@test.com",
    password: str = "Password1",
    tier: str = "free",
    verified: bool = True,
    name: str = "Test",
    with_profile: bool = True,
) -> tuple[User, dict]:
    """Create a user (+email provider, +profile) and return (user, auth headers)."""
    async with AsyncSessionLocal() as session:
        user = User(
            email=email,
            display_name=name,
            subscription_tier=tier,
            email_verified=verified,
        )
        session.add(user)
        await session.flush()
        if email:
            session.add(AuthProvider(
                user_id=user.id,
                provider="email",
                provider_id=email,
                password_hash=hash_password(password),
            ))
        if with_profile:
            from datetime import date
            session.add(UserProfile(user_id=user.id, birth_date=date(1995, 11, 8)))
        await session.commit()
        await session.refresh(user)

    headers = {"Authorization": f"Bearer {create_jwt(str(user.id))}"}
    return user, headers


@pytest_asyncio.fixture
async def auth_user():
    return await make_user()


@pytest_asyncio.fixture
async def auth_headers(auth_user):
    return auth_user[1]


@pytest_asyncio.fixture
async def pro_user():
    return await make_user(email="pro@test.com", tier="pro")


@pytest_asyncio.fixture
async def pro_headers(pro_user):
    return pro_user[1]


@pytest.fixture
def admin_headers():
    return {"X-Admin-Token": "test-admin-token"}


@pytest.fixture
def internal_headers():
    return {"X-Internal-Token": "test-admin-token"}
