from fastapi import FastAPI

from src.config import get_settings
from src.routes.auth import router as auth_router
from src.routes.tasks import router as tasks_router

settings = get_settings()
app = FastAPI(title=settings.app_name, version="2.0.0")
app.include_router(auth_router, prefix=settings.api_v1_prefix)
app.include_router(tasks_router, prefix=settings.api_v1_prefix)


@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok"}
