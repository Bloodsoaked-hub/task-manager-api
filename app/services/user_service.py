from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.repositories.user import UserRepository


class UserService:
    def __init__(self, db: Session):
        self.repo = UserRepository(db)

    def get_me(self, user_id: int):
        user = self.repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
