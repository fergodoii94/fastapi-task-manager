from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session
from src import services
from src.database import get_db
from src.schemas import TaskCreate, TaskPage, TaskRead, TaskStatus, TaskUpdate

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.post("", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate, db: Session = Depends(get_db)):
    return services.create_task(db, payload)

@router.get("", response_model=TaskPage)
def list_tasks(page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=100), task_status: TaskStatus | None = Query(None, alias="status"), db: Session = Depends(get_db)):
    total, items = services.list_tasks(db, page, page_size, task_status)
    return TaskPage(total=total, items=items, page=page, page_size=page_size)

@router.get("/{task_id}", response_model=TaskRead)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = services.get_task(db, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.patch("/{task_id}", response_model=TaskRead)
def update_task(task_id: int, payload: TaskUpdate, db: Session = Depends(get_db)):
    task = services.get_task(db, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return services.update_task(db, task, payload)

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = services.get_task(db, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    services.delete_task(db, task)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
