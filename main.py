from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

class Task(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    completed: bool = False

tasks = []

@app.post("/tasks/", response_model=Task)
def create_task(task: Task):
    tasks.append(task)
    return task

@app.get("/tasks/", response_model=List[Task])
def get_tasks():
    return tasks

@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: int):
    task = next((t for t in tasks if t.id == task_id), None)
    if not task: raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    global tasks
    tasks = [t for t in tasks if t.id != task_id]
    return {"message": "Task deleted successfully"}
