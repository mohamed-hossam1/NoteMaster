from abc import ABC, abstractmethod
from typing import List, Optional # Make sure List is imported here
from dataclasses import dataclass, field # Import field for default_factory


@dataclass
class SketchPoint:
    x: float
    y: float
    size: float
    red: float
    green: float
    blue: float
    opacity: float


@dataclass
class NoteImage:
    image_path: str
    # If you plan to have image_name separately, add it here
    # image_name: Optional[str] = None
    # def __post_init__(self):
    #     if self.image_name is None and self.image_path:
    #         import os
    #         self.image_name = os.path.basename(self.image_path)


@dataclass
class NoteAudio:
    audio_path: str
    # If you plan to have audio_name separately, add it here
    # audio_name: Optional[str] = None
    # def __post_init__(self):
    #     if self.audio_name is None and self.audio_path:
    #         import os
    #         self.audio_name = os.path.basename(self.audio_path)


@dataclass
class Note:
    id: int
    user_id: int
    note_name: str
    text_content: Optional[str] = ""
    is_secure: bool = False
    secure_password: Optional[str] = None
    # Use default_factory to initialize mutable defaults like lists
    image_paths: List[NoteImage] = field(default_factory=list)
    audio_paths: List[NoteAudio] = field(default_factory=list)
    sketch_points: List[SketchPoint] = field(default_factory=list)

    # The __post_init__ is not strictly necessary if using default_factory
    # but can be kept if there's other logic.
    # For simple list initialization, default_factory is cleaner.
    # def __post_init__(self):
    #     if self.image_paths is None: # This check is now handled by default_factory
    #         self.image_paths = []
    #     if self.audio_paths is None:
    #         self.audio_paths = []
    #     if self.sketch_points is None:
    #         self.sketch_points = []


@dataclass
class User:
    id: int
    username: str
    password: str  # Hashed password


class IDatabaseManager(ABC):
    @abstractmethod
    def get_connection(self):
        pass

    @abstractmethod
    def close(self):
        pass


class IUserRepository(ABC):
    @abstractmethod
    def get_all_users(self) -> List[User]:
        pass

    @abstractmethod
    def get_user_by_username(self, username: str) -> Optional[User]:
        pass

    @abstractmethod
    def add_user(self, username: str, hashed_password: str) -> User:
        pass


class INoteRepository(ABC):
    @abstractmethod
    def get_notes_by_user(self, user_id: int) -> List[Note]:
        pass

    @abstractmethod
    def create_note(self, user_id: int, note_name: str, text_content: str, is_secure: bool, secure_password: Optional[str]) -> Note:
        pass

    @abstractmethod
    def update_note_content(self, note_id: int, text_content: str):
        pass

    @abstractmethod
    def delete_note(self, note_id: int):
        pass

    @abstractmethod
    def note_name_exists(self, user_id: int, note_name: str) -> bool:
        pass

    @abstractmethod
    def add_image_to_note(self, note_id: int, image_path: str):
        pass

    @abstractmethod
    def remove_image_from_note(self, note_id: int, image_path: str):
        pass

    @abstractmethod
    def get_note_images(self, note_id: int) -> List[NoteImage]:
        pass

    @abstractmethod
    def add_audio_to_note(self, note_id: int, audio_path: str):
        pass

    # Added missing abstract method definition based on note_service.py usage
    @abstractmethod
    def remove_audio_from_note(self, note_id: int, audio_path: str):
        pass

    @abstractmethod
    def get_note_audio(self, note_id: int) -> List[NoteAudio]:
        pass

    @abstractmethod
    def add_sketch_point_to_note(self, note_id: int, point: SketchPoint):
        pass

    @abstractmethod
    def clear_sketch_points_for_note(self, note_id: int):
        pass

    @abstractmethod
    def get_note_sketch_points(self, note_id: int) -> List[SketchPoint]:
        pass