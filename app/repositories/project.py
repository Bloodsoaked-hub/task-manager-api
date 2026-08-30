from sqlalchemy.orm import Session
from app.models.project import Project
from app.repositories.base import BaseRepository


class ProjectRepository(BaseRepository[Project]):
    def __init__(self, db: Session):
        super().__init__(db, Project)

    def create_project(self, title: str, description: str | None, owner_id: int):
        project = Project(title=title, description=description, owner_id=owner_id)
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        return project

    def update_project(
        self, project: Project, title: str | None, description: str | None
    ):
        if title is not None:
            project.title = title
        if description is not None:
            project.description = description
        self.db.commit()
        self.db.refresh(project)
        return project

    def get_by_owner(self, owner_id: int):
        return self.db.query(Project).filter(Project.owner_id == owner_id).all()
