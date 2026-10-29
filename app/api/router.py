from fastapi import APIRouter

from app.api.routes import auth, projects, tasks, users, documents

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(projects.router)
api_router.include_router(tasks.router)
api_router.include_router(users.router)
api_router.include_router(documents.router)