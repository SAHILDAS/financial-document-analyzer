from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.health import router as health_router
from app.core.config import settings


app = FastAPI(
    title=settings.app_name,
    description="AI-powered financial document analysis prototype",
    version="0.1.0",
    debug=settings.app_debug,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(
    health_router,
    prefix="/api",
)


@app.get("/", tags=["Root"])
async def root() -> dict[str, str]:
    return {
        "service": settings.app_name,
        "version": "0.1.0",
        "status": "running",
    }