from datetime import datetime
from app.repositories.user_repository import UserRepository
from app.models.users import User
from app.repositories.oauth_repository import OAuthTokenRepository

class UserService:    
    def __init__(self):
        self.user_repository = UserRepository()

    def get_user(self, user_id: int):
        return self.user_repository.get_by_id(user_id)

    def create_user(self, email: str, name: str) -> User | None:
        try:
            return self.user_repository.create(name=name, email=email)
        except Exception:
            return None
    
    