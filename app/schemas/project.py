from pydantic import BaseModel, ConfigDict
from datetime import datetime


class ProjectCreate(BaseModel):
    title: str
    description: str | None = None


class ProjectUpdate(BaseModel):
    title: str | None = None
    description: str | None = None


class ProjectOut(BaseModel):
    id: int
    title: str
    description: str | None
    created_at: datetime
    owner_id: int

    model_config = ConfigDict(from_attributes=True, extra="ignore")
