from __future__ import annotations

import logging
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from src.auth import LoginRequest, create_access_token, get_current_user
from src.config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)
logger = logging.getLogger("task_manager")

app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="Production-ready FastAPI task manager with JWT auth and health monitoring.",
)


class Task(BaseModel):
    id: int
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    priority: int = Field(default=1, ge=1, le=5)
    completed: bool = False


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    priority: int = Field(default=1, ge=1, le=5)
    completed: bool = False


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = None
    priority: Optional[int] = Field(default=None, ge=1, le=5)
    completed: Optional[bool] = None


tasks_db: list[Task] = []


@app.exception_handler(HTTPException)
async def http_exception_handler(_, exc: HTTPException):
    logger.warning("HTTP error %s: %s", exc.status_code, exc.detail)
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(Exception)
async def generic_exception_handler(_, exc: Exception):
    logger.exception("Unhandled server error: %s", exc)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.get("/")
def root():
    return {"message": f"Welcome to {settings.app_name}", "docs": "/docs"}


@app.get("/health")
def health_check():
    return {"status": "ok", "service": settings.app_name, "version": settings.version}


@app.post("/login")
def login(payload: LoginRequest):
    if payload.username != settings.demo_username or payload.password != settings.demo_password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")

    token = create_access_token(payload.username)
    logger.info("User %s logged in successfully", payload.username)
    return {"access_token": token, "token_type": "bearer"}


@app.get("/me")
def read_current_user(current_user: dict[str, str] = Depends(get_current_user)):
    return {"username": current_user["sub"]}


@app.post("/tasks", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate, current_user: dict[str, str] = Depends(get_current_user)):
    task_id = max((t.id for t in tasks_db), default=0) + 1
    new_task = Task(
        id=task_id,
        title=task.title,
        description=task.description,
        priority=task.priority,
        completed=task.completed,
    )
    tasks_db.append(new_task)
    logger.info("Task %s created by %s", task_id, current_user["sub"])
    return new_task


@app.get("/tasks", response_model=list[Task])
def list_tasks(current_user: dict[str, str] = Depends(get_current_user)):
    logger.info("Listing tasks for %s", current_user["sub"])
    return tasks_db


@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: int, current_user: dict[str, str] = Depends(get_current_user)):
    logger.info("Fetching task %s for %s", task_id, current_user["sub"])
    for task in tasks_db:
        if task.id == task_id:
            return task
    raise HTTPException(status_code=404, detail="Task not found")


@app.put("/tasks/{task_id}", response_model=Task)
def update_task(
    task_id: int,
    patch: TaskUpdate,
    current_user: dict[str, str] = Depends(get_current_user),
):
    for index, task in enumerate(tasks_db):
        if task.id == task_id:
            updated_task = task.model_copy(update={
                k: v for k, v in patch.model_dump(exclude_unset=True).items() if v is not None
            })
            tasks_db[index] = updated_task
            logger.info("Task %s updated by %s", task_id, current_user["sub"])
            return updated_task
    raise HTTPException(status_code=404, detail="Task not found")


@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, current_user: dict[str, str] = Depends(get_current_user)):
    global tasks_db
    original_count = len(tasks_db)
    tasks_db = [task for task in tasks_db if task.id != task_id]
    if len(tasks_db) == original_count:
        raise HTTPException(status_code=404, detail="Task not found")
    logger.info("Task %s deleted by %s", task_id, current_user["sub"])
    return {"message": "Task deleted successfully"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
