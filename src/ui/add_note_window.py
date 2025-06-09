import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QLineEdit, QPushButton,
                             QFrame, QGraphicsDropShadowEffect, QCheckBox,
                             QMessageBox)
from PyQt5.QtCore import Qt, QPoint, QTimer
from PyQt5.QtGui import QFont, QColor

# Corrected imports for refactored structure
from src.core.interfaces import User, Note
from src.services.note_service import NoteService
from src.ui.shared_ui_components import ModernButton, ModernLineEdit
# from .note_window import NoteWindow # If NoteWindow is in the same directory


class AddNoteWindow(QMainWindow): # Consider using BaseWindow
    def __init__(self, user: User, note_service: NoteService, home_window_ref, secure_password_to_use=None):
        super().__init__()
        self.user = user
        self.note_service = note_service
        self.home_window_ref = home_window_ref
        self.is_secure_note_creation = secure_password_to_use is not None
        self.secure_password_to_use_for_creation = secure_password_to_use

        self.setWindowTitle("Add New Note - NoteMaster")
        self.setFixedSize(600, 500 if not self.is_secure_note_creation else 580)
        self.setWindowFlags(Qt.FramelessWindowHint)

        self.drag_position = QPoint()
        self.note_window_instance = None

        self.init_ui()

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        content_panel = self.create_content_panel()
        main_layout.addWidget(content_panel)

        self.setStyleSheet("""
            QMainWindow {
                background: white;
            }
        """)

    def create_content_panel(self):
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 0px; /* Changed from 10px in original to 0px for frameless */
            }
        """)

        layout = QVBoxLayout(panel)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(25)
        layout.setContentsMargins(40, 40, 40, 40)

        header_layout = QHBoxLayout()
        title_label = QLabel("Create New Note")
        title_label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                font-size: 24px;
                font-weight: bold;
                font-family: 'Arial', sans-serif;
            }
        """)

        close_button = QPushButton("×")
        close_button.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #666;
                border: none;
                font-size: 24px;
                font-weight: bold;
                padding: 5px;
            }
            QPushButton:hover {
                color: #ff4757;
                background: rgba(255, 71, 87, 0.1);
                border-radius: 15px;
            }
        """)
        close_button.setFixedSize(30, 30)
        close_button.clicked.connect(self.cancel_creation) # Renamed method

        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(close_button)
        layout.addLayout(header_layout)

        subtitle = QLabel("Enter the details for your new note")
        subtitle.setStyleSheet("""
            QLabel {
                color: #7f8c8d;
                font-size: 16px;
                font-family: 'Arial', sans-serif;
                margin-bottom: 20px;
            }
        """)
        layout.addWidget(subtitle)

        form_container = QWidget()
        form_layout = QVBoxLayout(form_container)
        form_layout.setSpacing(20)

        name_label = QLabel("Note Name")
        name_label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                font-size: 14px;
                font-weight: bold;
                margin-bottom: 5px;
            }
        """)
        self.name_field = ModernLineEdit("Enter a name for your note")
        form_layout.addWidget(name_label)
        form_layout.addWidget(self.name_field)

        if self.is_secure_note_creation:
            password_label = QLabel("Note Password")
            password_label.setStyleSheet(name_label.styleSheet()) # Reuse style
            self.password_display_field = ModernLineEdit("Password is set for this secure note")
            self.password_display_field.setEnabled(False) # Display only
            form_layout.addWidget(password_label)
            form_layout.addWidget(self.password_display_field)
            password_info = QLabel("This note will be encrypted and require this password to open.")
            password_info.setStyleSheet("""
                QLabel {
                    color: #7f8c8d; font-size: 12px; font-style: italic; margin-top: -10px;
                }
            """)
            form_layout.addWidget(password_info)

        layout.addWidget(form_container)
        layout.addStretch(1)

        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)
        cancel_button = ModernButton("Cancel", primary=False)
        cancel_button.setFixedWidth(150)
        cancel_button.clicked.connect(self.cancel_creation)
        create_button = ModernButton("Create Note")
        create_button.setFixedWidth(150)
        create_button.clicked.connect(self.process_create_note) # Renamed

        buttons_layout.addStretch()
        buttons_layout.addWidget(cancel_button)
        buttons_layout.addWidget(create_button)
        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)

        self.error_label = QLabel()
        self.error_label.setStyleSheet("""
            QLabel {
                color: #e74c3c; font-size: 12px; font-weight: bold;
                background: rgba(231, 76, 60, 0.1); padding: 10px;
                border-radius: 5px; border: 1px solid rgba(231, 76, 60, 0.3);
            }
        """)
        self.error_label.setAlignment(Qt.AlignCenter)
        self.error_label.hide()
        layout.addWidget(self.error_label)
        if not self.is_secure_note_creation:
             layout.addStretch(1)
        return panel

    def process_create_note(self):
        note_name = self.name_field.text().strip()
        if not note_name:
            self.show_error_message("Please enter a note name!")
            return

        try:
            new_note_obj: Note
            if self.is_secure_note_creation:
                if not self.secure_password_to_use_for_creation:
                    self.show_error_message("Secure password not set. Internal error.")
                    return
                new_note_obj = self.note_service.create_secure_note(
                    self.user.id, note_name, self.secure_password_to_use_for_creation
                )
            else:
                new_note_obj = self.note_service.create_note(self.user.id, note_name)

            self.hide()
            
            from src.ui.note_window import NoteWindow # Delayed import
            from src.services.user_folder_manager import UserFolderManager
            user_folder_manager = UserFolderManager(self.user.username) # Create UFM instance

            # NoteWindow will need to accept NoteService and UserFolderManager
            self.note_window_instance = NoteWindow(
                self.user, new_note_obj, self.note_service, user_folder_manager, home_window_ref=self.home_window_ref
            )
            self.note_window_instance.show()

            if self.home_window_ref:
                self.home_window_ref.load_notes() # Refresh notes in HomeWindow
            self.deleteLater()

        except ValueError as e: # e.g., note name exists
            self.show_error_message(str(e))
        except Exception as e:
            self.show_error_message(f"An unexpected error occurred: {e}")
            print(f"Error creating note: {e}")

    def cancel_creation(self):
        self.hide()
        if self.home_window_ref:
            self.home_window_ref.show()
        self.deleteLater()

    def show_error_message(self, message):
        self.error_label.setText(message)
        self.error_label.show()
        QTimer.singleShot(3000, self.error_label.hide)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.drag_position:
            self.move(event.globalPos() - self.drag_position)
            event.accept()

    def closeEvent(self, event):
        if self.home_window_ref and not self.home_window_ref.isVisible():
            self.home_window_ref.show()
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Setup for testing - this would typically be done by main.py
    from src.data.database_manager import SQLiteDatabaseManager
    from src.data.user_repository import SQLiteUserRepository
    from src.services.user_service import UserService
    from src.data.note_repository import SQLiteNoteRepository
    # HomeWindow for testing reference
    from src.ui.home_window import HomeWindow


    db_manager = SQLiteDatabaseManager()
    user_repo = SQLiteUserRepository()
    user_service = UserService(user_repo)
    note_repo = SQLiteNoteRepository()
    note_service = NoteService(note_repo)


    try:
        test_user = user_service.register_user("addnotetest", "password123")
    except ValueError:
        test_user = user_service.authenticate_user("addnotetest", "password123")

    if not test_user:
        print("Failed to create/login test user for AddNoteWindow.")
        sys.exit(1)

    # Dummy HomeWindow for testing reference
    dummy_home = HomeWindow(test_user, note_service)
    # dummy_home.show() # Don't show it here, AddNoteWindow will handle it

    # Test creating a regular note
    # add_note_win = AddNoteWindow(test_user, note_service, dummy_home)
    # add_note_win.show()

    # Test creating a secure note
    add_secure_note_win = AddNoteWindow(test_user, note_service, dummy_home, secure_password_to_use="securepass123")
    add_secure_note_win.show()
    dummy_home.hide() # Simulate home hiding when add note opens

    sys.exit(app.exec_())