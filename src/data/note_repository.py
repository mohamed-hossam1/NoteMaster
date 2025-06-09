import sqlite3
import os
from typing import List, Optional
from src.core.interfaces import INoteRepository, Note, NoteImage, NoteAudio, SketchPoint
from src.data.database_manager import SQLiteDatabaseManager


class SQLiteNoteRepository(INoteRepository):
    def __init__(self):
        self.db_manager = SQLiteDatabaseManager()

    def get_notes_by_user(self, user_id: int) -> List[Note]:
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, note_name, text_content, is_secure, secure_password
            FROM notes
            WHERE user_id = ?
        """, (user_id,))

        notes = []
        for row in cursor.fetchall():
            note_id, note_name, text_content, is_secure, secure_password = row
            # Fetch related data when constructing the Note object
            images = self.get_note_images(note_id)
            audios = self.get_note_audio(note_id)
            sketches = self.get_note_sketch_points(note_id)
            note = Note(
                id=note_id,
                user_id=user_id,
                note_name=note_name,
                text_content=text_content if text_content is not None else "",
                is_secure=bool(is_secure),
                secure_password=secure_password,
                image_paths=images,
                audio_paths=audios,
                sketch_points=sketches
            )
            notes.append(note)
        return notes

    def create_note(self, user_id: int, note_name: str, text_content: str, is_secure: bool, secure_password: Optional[str]) -> Note:
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO notes (user_id, note_name, text_content, is_secure, secure_password)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, note_name, text_content, int(is_secure), secure_password))
        conn.commit()
        note_id = cursor.lastrowid
        if note_id is None:
            raise Exception("Failed to create note, no ID returned.")
        # Return a Note object with empty lists for media/sketches, as they are added separately
        return Note(note_id, user_id, note_name, text_content, is_secure, secure_password, [], [], [])


    def update_note_content(self, note_id: int, text_content: str):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE notes
            SET text_content = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (text_content, note_id))
        conn.commit()

    def delete_note(self, note_id: int):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        # It's good practice to delete related records first to maintain integrity,
        # though cascading deletes could also be set up in the DB schema.
        cursor.execute("DELETE FROM sketch_points WHERE note_id = ?", (note_id,))
        cursor.execute("DELETE FROM images WHERE note_id = ?", (note_id,))
        cursor.execute("DELETE FROM audio WHERE note_id = ?", (note_id,))
        cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        conn.commit()

    def note_name_exists(self, user_id: int, note_name: str) -> bool:
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM notes
            WHERE user_id = ? AND note_name = ?
        """, (user_id, note_name))
        count = cursor.fetchone()[0] # fetchone() returns a tuple
        return count > 0

    def add_image_to_note(self, note_id: int, image_path: str):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO images (note_id, image_path) VALUES (?, ?)",
            (note_id, image_path)
        )
        conn.commit()

    def remove_image_from_note(self, note_id: int, image_path: str):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM images WHERE note_id = ? AND image_path = ?",
            (note_id, image_path)
        )
        conn.commit()

    def get_note_images(self, note_id: int) -> List[NoteImage]:
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT image_path FROM images WHERE note_id = ?", (note_id,))
        return [NoteImage(row[0]) for row in cursor.fetchall()]

    def add_audio_to_note(self, note_id: int, audio_path: str):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO audio (note_id, audio_path) VALUES (?, ?)",
            (note_id, audio_path)
        )
        conn.commit()

    # Implementation for the newly added interface method
    def remove_audio_from_note(self, note_id: int, audio_path: str):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM audio WHERE note_id = ? AND audio_path = ?",
            (note_id, audio_path)
        )
        conn.commit()

    def get_note_audio(self, note_id: int) -> List[NoteAudio]:
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT audio_path FROM audio WHERE note_id = ?", (note_id,))
        return [NoteAudio(row[0]) for row in cursor.fetchall()]

    def add_sketch_point_to_note(self, note_id: int, point: SketchPoint):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO sketch_points
            (note_id, x, y, size, red, green, blue, opacity)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            note_id, point.x, point.y, point.size,
            point.red, point.green, point.blue, point.opacity
        ))
        conn.commit()

    def clear_sketch_points_for_note(self, note_id: int):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sketch_points WHERE note_id = ?", (note_id,))
        conn.commit()

    def get_note_sketch_points(self, note_id: int) -> List[SketchPoint]:
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT x, y, size, red, green, blue, opacity
            FROM sketch_points
            WHERE note_id = ?
        """, (note_id,))
        # Ensure correct number of arguments for SketchPoint constructor
        return [SketchPoint(row[0], row[1], row[2], row[3], row[4], row[5], row[6]) for row in cursor.fetchall()]