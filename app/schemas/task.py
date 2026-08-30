from pydantic import BaseModel, ConfigDict
from datetime import datetime


class TaskCreate(BaseModel):
    title: str
    description: str | None = None


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None


class TaskOut(BaseModel):
    id: int
    title: str
    description: str | None
    is_done: bool
    created_at: datetime
    project_id: int

    model_config = ConfigDict(from_attributes=True, extra="ignore")


class TaskGenerateRequest(BaseModel):
    text: str
