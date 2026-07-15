import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

import app.models  # noqa: F401 — register models with SQLModel.metadata
from app.api.router import api_router
from app.core.database import create_db_and_tables
from app.core.redis import close_redis, init_redis
from app.scheduler import scheduler, send_daily_horoscopes, send_subscription_reminders, send_astro_event_notifications, cleanup_deleted_accounts, demote_expired_subscriptions


@asynccontextmanager
async def lifespan(_app: FastAPI):
    await create_db_and_tables()
    await init_redis()
    scheduler.add_job(
        send_daily_horoscopes,
        trigger="cron",
        minute="*/5",
        id="daily_horoscope",
        replace_existing=True,
    )
    scheduler.add_job(
        send_subscription_reminders,
        trigger="cron",
        hour=12,
        minute=0,
        id="subscription_reminders",
        replace_existing=True,
    )
    scheduler.add_job(
        demote_expired_subscriptions,
        trigger="cron",
        minute=0,
        id="demote_expired_subscriptions",
        replace_existing=True,
    )
    scheduler.add_job(
        send_astro_event_notifications,
        trigger="cron",
        hour=8,
        minute=0,
        id="astro_events",
        replace_existing=True,
    )
    scheduler.add_job(
        cleanup_deleted_accounts,
        trigger="cron",
        hour=3,
        minute=0,
        id="cleanup_deleted_accounts",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("Scheduler started: daily_horoscope (*/5min), subscription_reminders (12:00 UTC), demote_expired_subscriptions (hourly), cleanup_deleted_accounts (03:00 UTC)")
    import asyncio
    from app.core.seo_generator import warm_seo_cache
    asyncio.create_task(warm_seo_cache())
    yield
    scheduler.shutdown()
    await close_redis()


app = FastAPI(title="Mystral API", version="0.1.0", lifespan=lifespan)


@app.exception_handler(RequestValidationError)
async def validation_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    msgs = []
    for err in errors:
        field = " → ".join(str(loc) for loc in err.get("loc", []) if loc != "body")
        msgs.append(f"{field}: {err.get('msg', 'invalid')}")
    return JSONResponse(
        status_code=422,
        content={"error": "validation", "message": "; ".join(msgs) if msgs else "Ошибка валидации"},
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    detail = exc.detail
    if isinstance(detail, dict):
        return JSONResponse(status_code=exc.status_code, content=detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.status_code, "message": str(detail)},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error: %s", exc)
    return JSONResponse(
        status_code=500,
        content={"error": "server_error", "message": "Внутренняя ошибка сервера"},
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://mystral.space",
        "https://www.mystral.space",
        "https://web.telegram.org",
        "http://localhost:5173",
        "http://localhost:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

from app.api.v1.seo_pages import router as seo_router
app.include_router(seo_router)

