from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps.db import get_db
from app.api.deps.auth import get_current_user
from app.models.user import User
from app.services.task_service import TaskService
from app.schemas.task import TaskCreate, TaskOut, TaskUpdate, TaskGenerateRequest

router = APIRouter(prefix="/projects/{project_id}/tasks", tags=["tasks"])


@router.post("/", response_model=TaskOut)
def create_task(
    project_id: int,
    data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return TaskService(db).create_task(project_id, data, current_user.id)


@router.post("/generate", response_model=list[TaskOut])
def generate_task(
    project_id: int,
    data: TaskGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return TaskService(db).generate_tasks_from_text(
        project_id, data.text, current_user.id
    )


@router.patch("/{task_id}", response_model=TaskOut)
def update_task(
    task_id: int,
    data: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return TaskService(db).update_task(task_id, current_user.id, data)


@router.patch("/{task_id}/toggle", response_model=TaskOut)
def toggle_task_done(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return TaskService(db).toggle_done(task_id, current_user.id)


@router.get("/", response_model=list[TaskOut])
def list_tasks(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return TaskService(db).get_tasks_for_project(project_id, current_user.id)


@router.get("/search", response_model=list[TaskOut])
def search_tasks(
    project_id: int,
    q: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return TaskService(db).search_tasks(project_id, q, current_user.id)


@router.delete("/{task_id}", status_code=204)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return TaskService(db).delete_task(task_id, current_user.id)
