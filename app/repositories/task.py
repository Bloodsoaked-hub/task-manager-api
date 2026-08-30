from sqlalchemy.orm import Session

from app.models.task import Task
from app.repositories.base import BaseRepository


class TaskRepository(BaseRepository[Task]):
    def __init__(self, db: Session):
        super().__init__(db, Task)

    def create_task(
        self,
        title: str,
        description: str | None,
        project_id: int,
        embedding: list[float],
    ):
        task = Task(
            title=title,
            description=description,
            project_id=project_id,
            embedding=embedding,
        )
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def get_by_project(self, project_id: int):
        return self.db.query(Task).filter(Task.project_id == project_id).all()

    def update_task(self, task: Task, title: str | None, description: str | None):
        if title is not None:
            task.title = title
        if description is not None:
            task.description = description
        self.db.commit()
        self.db.refresh(task)
        return task

    def toggle_done(self, task: Task):
        task.is_done = not task.is_done
        self.db.commit()
        self.db.refresh(task)
        return task

    def search_similar(
        self, project_id: int, query_embedding: list[float], limit: int = 5
    ):
        return (
            self.db.query(Task)
            .filter(Task.project_id == project_id)
            .order_by(Task.embedding.cosine_distance(query_embedding))
            .limit(limit)
            .all()
        )
