from fastapi import APIRouter

from app.api import investigations, rca

api_router = APIRouter()
api_router.include_router(rca.router, prefix="/rca", tags=["RCA AI workflow"])
api_router.include_router(investigations.router, prefix="/investigations", tags=["Investigations"])
