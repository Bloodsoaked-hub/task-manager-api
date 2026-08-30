from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.project import ProjectRepository
from app.schemas.project import ProjectCreate, ProjectUpdate


class ProjectService:
    def __init__(self, db: Session):
        self.repo = ProjectRepository(db)

    def create_project(self, data: ProjectCreate, owner_id: int):
        return self.repo.create_project(
            title=data.title, description=data.description, owner_id=owner_id
        )

    def get_projects_for_owner(self, owner_id: int):
        return self.repo.get_by_owner(owner_id)

    def get_project(self, project_id: int, owner_id: int):
        project = self.repo.get_by_id(project_id)
        if not project or project.owner_id != owner_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
            )
        return project

    def update_project(self, project_id: int, owner_id: int, data: ProjectUpdate):
        project = self.get_project(project_id, owner_id)
        return self.repo.update_project(project, data.title, data.description)

    def delete_project(self, project_id: int, owner_id: int):
        project = self.get_project(project_id, owner_id)
        self.repo.delete(project)
