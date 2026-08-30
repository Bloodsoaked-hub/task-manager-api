from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.repositories.user import UserRepository
from app.core.security import hash_password, verify_password, create_access_token
from app.schemas.auth import LoginRequest, Token
from app.schemas.user import UserCreate


class AuthService:
    def __init__(self, db: Session):
        self.repo = UserRepository(db)

    def register(self, data: UserCreate):
        existing_user = self.repo.get_by_email(data.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        hashed_password = hash_password(data.password)
        return self.repo.create_user(email=data.email, hashed_password=hashed_password)

    def login(self, data: LoginRequest) -> Token:
        user = self.repo.get_by_email(data.email)
        if not user or not verify_password(data.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        access_token = create_access_token(sub=str(user.id))
        return Token(access_token=access_token, token_type="bearer")
