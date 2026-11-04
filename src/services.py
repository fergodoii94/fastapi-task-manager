from sqlalchemy import func, select
from sqlalchemy.orm import Session
from src.models import Task
from src.schemas import TaskCreate, TaskUpdate, TaskStatus

def create_task(db: Session, payload: TaskCreate) -> Task:
    task = Task(**payload.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

def list_tasks(db: Session, page: int, page_size: int, status: TaskStatus | None = None):
    query = select(Task)
    count_query = select(func.count()).select_from(Task)
    if status is not None:
        query = query.where(Task.status == status.value)
        count_query = count_query.where(Task.status == status.value)
    total = db.scalar(count_query) or 0
    items = list(db.scalars(query.order_by(Task.created_at.desc(), Task.id.desc()).offset((page - 1) * page_size).limit(page_size)))
    return total, items

def get_task(db: Session, task_id: int) -> Task | None:
    return db.get(Task, task_id)

def update_task(db: Session, task: Task, payload: TaskUpdate) -> Task:
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(task, field, value.value if isinstance(value, TaskStatus) else value)
    db.commit()
    db.refresh(task)
    return task

def delete_task(db: Session, task: Task) -> None:
    db.delete(task)
    db.commit()
