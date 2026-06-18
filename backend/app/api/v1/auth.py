from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/telegram")
async def auth_telegram():
    return {"detail": "not implemented"}


@router.post("/refresh")
async def refresh_token():
    return {"detail": "not implemented"}


@router.post("/logout")
async def logout():
    return {"detail": "not implemented"}
