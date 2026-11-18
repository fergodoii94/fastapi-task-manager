from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.models import Task, User
from src.schemas import TaskCreate, TaskStatus, TaskUpdate, UserCreate
from src.security import hash_password


def create_user(db: Session, payload: UserCreate) -> User:
    user = User(email=payload.email, password_hash=hash_password(payload.password))
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise
    db.refresh(user)
    return user


def create_task(db: Session, payload: TaskCreate, user_id: int) -> Task:
    task = Task(**payload.model_dump(), user_id=user_id)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def list_tasks(
    db: Session,
    user_id: int,
    page: int,
    page_size: int,
    status: TaskStatus | None = None,
) -> tuple[int, list[Task]]:
    query = select(Task).where(Task.user_id == user_id)
    count_query = select(func.count()).select_from(Task).where(Task.user_id == user_id)

    if status is not None:
        query = query.where(Task.status == status.value)
        count_query = count_query.where(Task.status == status.value)

    total = db.scalar(count_query) or 0
    items = list(
        db.scalars(
            query.order_by(Task.created_at.desc(), Task.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
    )
    return total, items


def get_task(db: Session, task_id: int, user_id: int) -> Task | None:
    return db.scalar(select(Task).where(Task.id == task_id, Task.user_id == user_id))


def update_task(db: Session, task: Task, payload: TaskUpdate) -> Task:
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(task, field, value.value if isinstance(value, TaskStatus) else value)
    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, task: Task) -> None:
    db.delete(task)
    db.commit()
