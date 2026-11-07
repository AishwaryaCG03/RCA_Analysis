from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import get_settings
from app.database.session import Base, engine
import app.models  # noqa: F401 - registers SQLAlchemy metadata

settings = get_settings()
app = FastAPI(title=settings.app_name, version="1.0.0", description="Human-reviewed AI-assisted Root Cause Analysis")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
app.include_router(api_router, prefix=settings.api_prefix)


@app.on_event("startup")
def create_local_tables() -> None:
    # Alembic is used for deployed databases. This keeps a fresh local SQLite demo runnable.
    if settings.database_url.startswith("sqlite"):
        Base.metadata.create_all(bind=engine)


@app.get("/health")
def health():
    return {"status": "ok", "ai_configured": bool(settings.groq_api_key), "model": settings.groq_model}
