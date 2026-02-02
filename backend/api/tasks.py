from fastapi import APIRouter, HTTPException, Depends, Body
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime
from backend.db.sqlite import get_db
from backend.db.models import Task, Project, Idea
from pydantic import BaseModel

router = APIRouter(prefix="/api/tasks", tags=["tasks"])

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    due_datetime: Optional[datetime] = None
    importance: int = 1
    severity: int = 1
    linked_project_id: Optional[int] = None
    linked_idea_id: Optional[int] = None
    task_type: str = "generic"

@router.post("/create")
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    if not task.linked_project_id and not task.linked_idea_id:
        raise HTTPException(status_code=400, detail="Task must be linked to a Project or Idea")
        
    new_task = Task(
        title=task.title,
        description=task.description,
        due_datetime=task.due_datetime,
        importance=task.importance,
        severity=task.severity,
        linked_project_id=task.linked_project_id,
        linked_idea_id=task.linked_idea_id,
        task_type=task.task_type,
        status="pending"
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

@router.get("/")
def list_tasks(
    project_id: Optional[int] = None, 
    idea_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Task)
    if project_id:
        query = query.filter(Task.linked_project_id == project_id)
    if idea_id:
        query = query.filter(Task.linked_idea_id == idea_id)
    if status:
        query = query.filter(Task.status == status)
        
    # Default sort by urgency (deadline) then severity * importance
    # For now simple due_date sort
    return query.order_by(Task.due_datetime.asc()).all()

@router.patch("/{id}")
def update_task(id: int, updates: dict = Body(...), db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    for key, value in updates.items():
        if hasattr(task, key):
            setattr(task, key, value)
            
    db.commit()
    db.refresh(task)
    return task
