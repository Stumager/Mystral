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
from app.scheduler import scheduler, send_daily_horoscopes, send_subscription_reminders, send_astro_event_notifications


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
        send_astro_event_notifications,
        trigger="cron",
        hour=8,
        minute=0,
        id="astro_events",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("Scheduler started: daily_horoscope (*/5min), subscription_reminders (12:00 UTC)")
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
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
