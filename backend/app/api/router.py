from fastapi import APIRouter

from app.api.v1 import auth, health
from app.api.v1.horoscope import router as horoscope_router

api_router = APIRouter()

api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router)
api_router.include_router(horoscope_router, prefix="/v1", tags=["horoscope"])
