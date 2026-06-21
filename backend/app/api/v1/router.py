from fastapi import APIRouter

from app.api.v1 import ai_agent, auth

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(ai_agent.router, prefix="/ai_agent", tags=["ai_agent"])
