from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.config import get_settings
from src.database import Base, engine
from src.routes.tasks import router as tasks_router
import src.models  # noqa: F401 - register SQLAlchemy models

@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

settings = get_settings()
app = FastAPI(title=settings.app_name, version="1.0.0", lifespan=lifespan)
app.include_router(tasks_router, prefix=settings.api_v1_prefix)

@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok"}
