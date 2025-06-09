import bcrypt


class PasswordUtils:
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt"""
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """Verify a password against a bcrypt hash"""
        return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))


