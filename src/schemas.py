from datetime import datetime
from enum import Enum
from pydantic import BaseModel, ConfigDict, Field

class TaskStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    archived = "archived"

class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=160)
    description: str | None = Field(default=None, max_length=5000)
    status: TaskStatus = TaskStatus.pending
    priority: int = Field(default=3, ge=1, le=5)

class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=160)
    description: str | None = Field(default=None, max_length=5000)
    status: TaskStatus | None = None
    priority: int | None = Field(default=None, ge=1, le=5)

class TaskRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    description: str | None
    status: TaskStatus
    priority: int
    created_at: datetime
    updated_at: datetime

class TaskPage(BaseModel):
    total: int
    items: list[TaskRead]
    page: int
    page_size: int
