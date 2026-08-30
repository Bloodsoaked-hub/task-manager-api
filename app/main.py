from fastapi import FastAPI

from app.api.router import api_router
from app.core.database import Base, engine
import app.models

app = FastAPI(title="Task Manager API")

Base.metadata.create_all(bind=engine)

app.include_router(api_router)
