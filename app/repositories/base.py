from sqlalchemy.orm import Session
from typing import Type, TypeVar, Generic

T = TypeVar("T")


class BaseRepository(Generic[T]):
    def __init__(self, db: Session, model: Type[T]):
        self.db = db
        self.model = model

    def get_by_id(self, id: int):
        return self.db.query(self.model).filter(self.model.id == id).first()

    def get_all(self):
        return self.db.query(self.model).all()

    def delete(self, obj: T):
        self.db.delete(obj)
        self.db.commit()
