import os


class UserFolderManager:
    def __init__(self, username: str):
        self.username = username
        self.folder_path = os.path.join("data", "users", username)
        self._ensure_folder_exists()

    def _ensure_folder_exists(self):
        os.makedirs(self.folder_path, exist_ok=True)
        os.makedirs(os.path.join(self.folder_path, "images"), exist_ok=True)
        os.makedirs(os.path.join(self.folder_path, "audio"), exist_ok=True)

    def get_images_path(self) -> str:
        return os.path.join(self.folder_path, "images") + os.sep

    def get_audio_path(self) -> str:
        return os.path.join(self.folder_path, "audio") + os.sep


