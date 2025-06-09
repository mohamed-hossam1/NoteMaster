import sqlite3
import os
from src.core.interfaces import IDatabaseManager


class SQLiteDatabaseManager(IDatabaseManager):
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SQLiteDatabaseManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self.db_path = "data/notes_app.db"
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            note_name TEXT NOT NULL,
            text_content TEXT DEFAULT '',
            is_secure INTEGER DEFAULT 0,
            secure_password TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            UNIQUE (user_id, note_name)
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            note_id INTEGER NOT NULL,
            image_path TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (note_id) REFERENCES notes (id)
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS audio (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            note_id INTEGER NOT NULL,
            audio_path TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (note_id) REFERENCES notes (id)
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS sketch_points (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            note_id INTEGER NOT NULL,
            x REAL NOT NULL,
            y REAL NOT NULL,
            size REAL NOT NULL,
            red REAL NOT NULL,
            green REAL NOT NULL,
            blue REAL NOT NULL,
            opacity REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (note_id) REFERENCES notes (id)
        )
        """)

        self.conn.commit()

    def get_connection(self):
        return self.conn

    def close(self):
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()