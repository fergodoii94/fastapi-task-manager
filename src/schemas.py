from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator


class UserCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: EmailStr
    password: str = Field(min_length=12, max_length=128)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.strip().lower()


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    created_at: datetime


class TokenRead(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: EmailStr
    password: str


class TaskStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    archived = "archived"


class TaskCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=160)
    description: str | None = Field(default=None, max_length=5000)
    status: TaskStatus = TaskStatus.pending
    priority: int = Field(default=3, ge=1, le=5)

    @field_validator("title")
    @classmethod
    def normalize_title(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Title must contain at least one non-whitespace character")
        return value


class TaskUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str | None = Field(default=None, min_length=1, max_length=160)
    description: str | None = Field(default=None, max_length=5000)
    status: TaskStatus | None = None
    priority: int | None = Field(default=None, ge=1, le=5)

    @field_validator("title")
    @classmethod
    def normalize_title(cls, value: str | None) -> str | None:
        if value is None:
            return value
        value = value.strip()
        if not value:
            raise ValueError("Title must contain at least one non-whitespace character")
        return value

    @model_validator(mode="after")
    def validate_patch(self) -> TaskUpdate:
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided")
        for field in ("title", "status", "priority"):
            if field in self.model_fields_set and getattr(self, field) is None:
                raise ValueError(f"{field} cannot be null")
        return self


class TaskRead(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid")

    id: int
    user_id: int
    title: str
    description: str | None
    status: TaskStatus
    priority: int
    created_at: datetime
    updated_at: datetime


class TaskPage(BaseModel):
    total: int = Field(ge=0)
    items: list[TaskRead]
    page: int = Field(ge=1)
    page_size: int = Field(ge=1, le=100)
