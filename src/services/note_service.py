import os
# from typing import List, Optional # List and Optional already imported via interfaces
from src.core.interfaces import INoteRepository, Note, NoteImage, NoteAudio, SketchPoint, User # <--- IMPORT User HERE
from src.services.user_folder_manager import UserFolderManager
from src.core.security_utils import PasswordUtils
from typing import List, Optional # Ensure these are available if not fully covered by interfaces import


class NoteService:
    def __init__(self, note_repository: INoteRepository):
        self.note_repository = note_repository

    def get_notes_for_user(self, user_id: int) -> List[Note]:
        return self.note_repository.get_notes_by_user(user_id)

    def _get_note_by_id(self, note_id: int, user_id: int) -> Optional[Note]:
        notes = self.note_repository.get_notes_by_user(user_id)
        for note in notes:
            if note.id == note_id:
                # These are already loaded by get_notes_by_user in the updated SQLiteNoteRepository
                # if not note.image_paths: 
                #     note.image_paths = self.note_repository.get_note_images(note_id)
                # if not note.audio_paths:
                #     note.audio_paths = self.note_repository.get_note_audio(note_id)
                # if not note.sketch_points:
                #      note.sketch_points = self.note_repository.get_note_sketch_points(note_id)
                return note
        return None


    def create_note(self, user_id: int, note_name: str, text_content: str = "") -> Note:
        if self.note_repository.note_name_exists(user_id, note_name):
            raise ValueError(f"Note name \'{note_name}\' already exists for this user.")
        return self.note_repository.create_note(user_id, note_name, text_content, False, None)

    def create_secure_note(self, user_id: int, note_name: str, password: str, text_content: str = "") -> Note:
        if self.note_repository.note_name_exists(user_id, note_name):
            raise ValueError(f"Note name \'{note_name}\' already exists for this user.")
        hashed_password = PasswordUtils.hash_password(password)
        return self.note_repository.create_note(user_id, note_name, text_content, True, hashed_password)

    def update_note_content(self, note_id: int, text_content: str):
        self.note_repository.update_note_content(note_id, text_content)

    def delete_note(self, note_id: int, user: User): 
        note_to_delete = self._get_note_by_id(note_id, user.id)

        if note_to_delete:
            user_folder_manager = UserFolderManager(user.username)
            for img_obj in note_to_delete.image_paths:
                try:
                    if os.path.exists(img_obj.image_path):
                        os.remove(img_obj.image_path)
                        print(f"Deleted image file: {img_obj.image_path}")
                except OSError as e:
                    print(f"Error deleting image file {img_obj.image_path}: {e}")
            
            for audio_obj in note_to_delete.audio_paths:
                try:
                    if os.path.exists(audio_obj.audio_path):
                        os.remove(audio_obj.audio_path)
                        print(f"Deleted audio file: {audio_obj.audio_path}")
                except OSError as e:
                    print(f"Error deleting audio file {audio_obj.audio_path}: {e}")
        else:
            print(f"Note with ID {note_id} not found for user {user.username} to delete associated files.")

        self.note_repository.delete_note(note_id)


    def add_image_to_note(self, note_id: int, image_path: str):
        self.note_repository.add_image_to_note(note_id, image_path)

    def remove_image_from_note(self, note_id: int, image_path: str):
        self.note_repository.remove_image_from_note(note_id, image_path)

    def add_audio_to_note(self, note_id: int, audio_path: str):
        self.note_repository.add_audio_to_note(note_id, audio_path)

    def remove_audio_from_note(self, note_id: int, audio_path: str):
        self.note_repository.remove_audio_from_note(note_id, audio_path)


    def add_sketch_point_to_note(self, note_id: int, point: SketchPoint):
        self.note_repository.add_sketch_point_to_note(note_id, point)

    def clear_sketch_points_for_note(self, note_id: int):
        self.note_repository.clear_sketch_points_for_note(note_id)

    def verify_secure_note_password(self, note: Note, password: str) -> bool:
        if not note.is_secure or not note.secure_password:
            return False
        return PasswordUtils.verify_password(password, note.secure_password)