from uuid import UUID
from typing import Optional

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.users import User

class UserRepository:

    def __init__(self, db: Optional[Session] = None):
        self.db = db or SessionLocal()

    def createUser(self, name: str, email: Optional[str] = None) -> Optional[User]:
            existing_user = self.db.query(User).filter(User.email == email).first()
            if existing_user:
                return existing_user
            user = User(name=name, email=email)
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            return user

    def get_by_id(self, user_id: UUID) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def list_all(self) -> list[User]:
        return self.db.query(User).all()
