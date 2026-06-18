from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import app.models  # noqa: F401 — register models with SQLModel.metadata
from app.api.router import api_router
from app.core.database import create_db_and_tables
from app.core.redis import close_redis, init_redis


@asynccontextmanager
async def lifespan(_app: FastAPI):
    await create_db_and_tables()
    await init_redis()
    yield
    await close_redis()


app = FastAPI(title="Mystral API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
