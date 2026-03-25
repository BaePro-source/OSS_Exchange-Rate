from fastapi import APIRouter

from backend.app.api.routes import auth, health, rates


api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(rates.router, prefix="/rates", tags=["rates"])
