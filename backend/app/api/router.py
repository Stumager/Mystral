from fastapi import APIRouter

from app.api.v1 import auth, health
from app.api.v1.horoscope import router as horoscope_router
from app.api.v1.natal import router as natal_router
from app.api.v1.profile import router as profile_router
from app.api.v1.tarot import router as tarot_router

api_router = APIRouter()

api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, prefix="/v1")
api_router.include_router(horoscope_router, prefix="/v1", tags=["horoscope"])
api_router.include_router(tarot_router, prefix="/v1", tags=["tarot"])
api_router.include_router(natal_router, prefix="/v1", tags=["natal"])
api_router.include_router(profile_router, prefix="/v1", tags=["profile"])
