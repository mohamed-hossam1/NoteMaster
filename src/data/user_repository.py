import sqlite3
from typing import List, Optional
from src.core.interfaces import IUserRepository, User
from src.data.database_manager import SQLiteDatabaseManager


class SQLiteUserRepository(IUserRepository):
    def __init__(self):
        self.db_manager = SQLiteDatabaseManager()

    def get_all_users(self) -> List[User]:
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, password FROM users")
        users = []
        for row in cursor.fetchall():
            users.append(User(row[0], row[1], row[2]))
        return users

    def get_user_by_username(self, username: str) -> Optional[User]:
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, password FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        if row:
            return User(row[0], row[1], row[2])
        return None

    def add_user(self, username: str, hashed_password: str) -> User:
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, hashed_password)
            )
            conn.commit()
            user_id = cursor.lastrowid
            if user_id is None:
                raise Exception("Failed to add user, no ID returned.")
            return User(user_id, username, hashed_password)
        except sqlite3.IntegrityError:
            raise ValueError(f"Username \'{username}\' already exists")


