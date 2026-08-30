from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.services.llm_service import LLMService
from app.repositories.task import TaskRepository
from app.services.project_service import ProjectService
from app.schemas.task import TaskCreate, TaskUpdate
from app.services.embedding_service import EmbeddingService


class TaskService:
    def __init__(self, db: Session):
        self.repo = TaskRepository(db)
        self.project_service = ProjectService(db)
        self.llm_service = LLMService()
        self.embedding_service = EmbeddingService()

    def create_task(self, project_id: int, data: TaskCreate, owner_id: int):
        self.project_service.get_project(project_id, owner_id)

        embedding_text = f"{data.title} {data.description or ''}".strip()
        embedding = self.embedding_service.generate_embedding(embedding_text)

        return self.repo.create_task(
            title=data.title,
            description=data.description,
            project_id=project_id,
            embedding=embedding,
        )

    def generate_tasks_from_text(self, project_id: int, text: str, owner_id: int):
        self.project_service.get_project(project_id, owner_id)

        parsed_tasks = self.llm_service.parse_tasks_from_text(text)

        created_tasks = []
        for task_data in parsed_tasks:
            embedding_text = f"{task_data.title} {task_data.description or ''}".strip()
            embedding = self.embedding_service.generate_embedding(embedding_text)
            created_task = self.repo.create_task(
                title=task_data.title,
                description=task_data.description,
                project_id=project_id,
                embedding=embedding,
            )
            created_tasks.append(created_task)

        return created_tasks

    def get_tasks_for_project(self, project_id: int, owner_id: int):
        self.project_service.get_project(project_id, owner_id)
        return self.repo.get_by_project(project_id)

    def update_task(self, task_id: int, owner_id: int, data: TaskUpdate):
        task = self.repo.get_by_id(task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
            )
        self.project_service.get_project(task.project_id, owner_id)
        return self.repo.update_task(task, data.title, data.description)

    def toggle_done(self, task_id: int, owner_id: int):
        task = self.repo.get_by_id(task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
            )
        self.project_service.get_project(task.project_id, owner_id)
        return self.repo.toggle_done(task)

    def delete_task(self, task_id: int, owner_id: int):
        task = self.repo.get_by_id(task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
            )
        self.project_service.get_project(task.project_id, owner_id)
        self.repo.delete(task)

    def search_tasks(self, project_id: int, query: str, owner_id: int):
        self.project_service.get_project(project_id, owner_id)

        query_embedding = self.embedding_service.generate_embedding(query)

        return self.repo.search_similar(project_id, query_embedding)
