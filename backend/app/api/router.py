from fastapi import APIRouter

from app.api.v1 import auth, health
from app.api.v1.admin import router as admin_router
from app.api.v1.compatibility import router as compatibility_router
from app.api.v1.horoscope import router as horoscope_router
from app.api.v1.lunar import router as lunar_router
from app.api.v1.natal import router as natal_router
from app.api.v1.numerology import router as numerology_router
from app.api.v1.push import router as push_router
from app.api.v1.payments import router as payments_router
from app.api.v1.profile import router as profile_router
from app.api.v1.runes import router as runes_router
from app.api.v1.tarot import router as tarot_router

api_router = APIRouter()

api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, prefix="/v1")
api_router.include_router(horoscope_router, prefix="/v1", tags=["horoscope"])
api_router.include_router(tarot_router, prefix="/v1", tags=["tarot"])
api_router.include_router(natal_router, prefix="/v1", tags=["natal"])
api_router.include_router(profile_router, prefix="/v1", tags=["profile"])
api_router.include_router(payments_router, prefix="/v1", tags=["payments"])
api_router.include_router(lunar_router, prefix="/v1", tags=["lunar"])
api_router.include_router(compatibility_router, prefix="/v1", tags=["compatibility"])
api_router.include_router(numerology_router, prefix="/v1", tags=["numerology"])
api_router.include_router(runes_router, prefix="/v1", tags=["runes"])
api_router.include_router(admin_router, prefix="/v1", tags=["admin"])
api_router.include_router(push_router, prefix="/v1", tags=["push"])
