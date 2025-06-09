from typing import Optional, List
from src.core.interfaces import User, IUserRepository
from src.core.security_utils import PasswordUtils


class UserService:
    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository

    def authenticate_user(self, username, password) -> Optional[User]:
        user = self.user_repository.get_user_by_username(username)
        if user and PasswordUtils.verify_password(password, user.password):
            return user
        return None

    def register_user(self, username, password) -> User:
        if self.user_repository.get_user_by_username(username):
            raise ValueError(f"Username \'{username}\' already exists")
        hashed_password = PasswordUtils.hash_password(password)
        return self.user_repository.add_user(username, hashed_password)

    def get_all_users(self) -> List[User]:
        return self.user_repository.get_all_users()


