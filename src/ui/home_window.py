import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QPushButton, QListWidget,
                             QFrame, QGraphicsDropShadowEffect, QMessageBox,
                             QInputDialog, QListWidgetItem, QGridLayout,
                             QScrollArea, QSizePolicy, QLineEdit)
from PyQt5.QtCore import Qt, QPoint, QSize
from PyQt5.QtGui import QFont, QPixmap, QColor, QIcon

# Corrected imports for refactored structure
from src.core.interfaces import User, Note # Assuming Note also includes SecureNote concept or handled by NoteService
from src.services.note_service import NoteService
from src.services.user_folder_manager import UserFolderManager
from src.core.security_utils import PasswordUtils # For SecureNote password verification if not in NoteService

# UI component imports - assuming these are now in shared_ui_components
from src.ui.shared_ui_components import ModernButton # Using the refactored ModernButton
# from .add_note_window import AddNoteWindow # If add_note_window is in the same dir
# from .note_window import NoteWindow # If note_window is in the same dir

# Placeholder for refactored AddNoteWindow and NoteWindow.
# These will need to be created in src/ui/ and their imports adjusted.
# For now, we'll use delayed imports for them.


class ModernCard(QFrame): # This class can stay or be moved to shared_ui_components if used elsewhere
    def __init__(self, title, subtitle="", icon_path=""):
        super().__init__()
        self.setFixedSize(280, 120)
        self.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 15px;
                border: 1px solid rgba(0, 0, 0, 0.1);
            }
            QFrame:hover {
                background: #f8f9fa;
                border: 1px solid #667eea;
            }
        """)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 5)
        self.setGraphicsEffect(shadow)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(10)

        top_layout = QHBoxLayout()

        icon_label = QLabel()
        if icon_path and os.path.exists(icon_path):
            pixmap = QPixmap(icon_path)
            scaled_pixmap = pixmap.scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            icon_label.setPixmap(scaled_pixmap)
        else:
            icon_label.setText("📄") # Default icon
            icon_label.setStyleSheet("QLabel { font-size: 24px; color: #667eea; }")

        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                font-size: 16px;
                font-weight: bold;
                font-family: 'Arial', sans-serif;
            }
        """)

        top_layout.addWidget(icon_label)
        top_layout.addWidget(title_label)
        top_layout.addStretch()
        layout.addLayout(top_layout)

        if subtitle:
            subtitle_label = QLabel(subtitle)
            subtitle_label.setStyleSheet("""
                QLabel {
                    color: #7f8c8d;
                    font-size: 12px;
                    font-family: 'Arial', sans-serif;
                }
            """)
            subtitle_label.setWordWrap(True)
            layout.addWidget(subtitle_label)

        layout.addStretch()


class HomeWindow(QMainWindow): # BaseWindow can be used here too
    def __init__(self, user: User, note_service: NoteService): # Inject NoteService
        super().__init__()
        self.user = user
        self.note_service = note_service
        self.user_folder_manager = UserFolderManager(user.username) # For file paths

        self.setWindowTitle(f"NoteMaster - Welcome {user.username}")
        self.setFixedSize(1400, 800) # Consider making this flexible or from BaseWindow
        self.setWindowFlags(Qt.FramelessWindowHint)

        self.drag_position = QPoint()
        self.add_note_window_instance = None
        self.note_window_instance = None
        self.login_window_instance = None # To go back to login

        self.init_ui()

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        header = self.create_header()
        main_layout.addWidget(header)

        content = self.create_content()
        main_layout.addWidget(content)

        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #f8f9fa, stop:1 #e9ecef);
            }
        """)
        self.load_notes() # Load notes initially

    def create_header(self):
        header = QFrame()
        header.setFixedHeight(80)
        header.setStyleSheet("""
            QFrame {
                background: white;
                border-bottom: 1px solid rgba(0, 0, 0, 0.1);
            }
        """)

        layout = QHBoxLayout(header)
        layout.setContentsMargins(30, 0, 30, 0)

        logo_layout = QHBoxLayout()
        # Correct asset path
        note_icon_path = os.path.join(os.path.dirname(__file__), "assets", "note.png")
        logo_label = QLabel()
        if os.path.exists(note_icon_path):
            pixmap = QPixmap(note_icon_path)
            scaled_pixmap = pixmap.scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)
        else:
            logo_label.setText("📝")
            logo_label.setStyleSheet("QLabel { font-size: 32px; color: #667eea; }")

        app_name = QLabel("NoteMaster")
        app_name.setStyleSheet("""
            QLabel {
                color: #2c3e50; font-size: 24px; font-weight: bold;
                font-family: 'Arial', sans-serif; margin-left: 10px;
            }
        """)
        logo_layout.addWidget(logo_label)
        logo_layout.addWidget(app_name)
        logo_layout.addStretch()
        layout.addLayout(logo_layout)

        user_layout = QHBoxLayout()
        welcome_label = QLabel(f"Welcome back, {self.user.username}!")
        welcome_label.setStyleSheet("""
            QLabel {
                color: #2c3e50; font-size: 16px; font-weight: 500;
                font-family: 'Arial', sans-serif; margin-right: 20px;
            }
        """)

        signout_button = ModernButton("Sign Out", primary=False)
        signout_button.setFixedWidth(120)
        signout_button.setStyleSheet(signout_button.styleSheet().replace("text-align: left;", "text-align: center;"))
        signout_button.clicked.connect(self.sign_out)

        close_button = QPushButton("×")
        close_button.setStyleSheet("""
            QPushButton {
                background: transparent; color: #666; border: none;
                font-size: 24px; font-weight: bold; padding: 5px;
            }
            QPushButton:hover { color: #ff4757; background: rgba(255, 71, 87, 0.1); border-radius: 15px; }
        """)
        close_button.setFixedSize(30, 30)
        close_button.clicked.connect(self.close_application)

        user_layout.addWidget(welcome_label)
        user_layout.addWidget(signout_button)
        user_layout.addWidget(close_button)
        layout.addLayout(user_layout)
        return header

    def create_content(self):
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(30)
        stats_section = self.create_stats_section()
        layout.addWidget(stats_section)
        notes_section = self.create_notes_section()
        layout.addWidget(notes_section)
        return content

    def create_stats_section(self):
        section = QWidget()
        layout = QVBoxLayout(section)
        layout.setSpacing(20)
        title = QLabel("Quick Actions")
        title.setStyleSheet("""
            QLabel {
                color: #2c3e50; font-size: 24px; font-weight: bold;
                font-family: 'Arial', sans-serif; margin-bottom: 10px;
            }
        """)
        layout.addWidget(title)
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(20)

        addnote_icon_path = os.path.join(os.path.dirname(__file__), "assets", "addnote.png")
        add_button = ModernButton(" New Note", primary=True, icon_path=addnote_icon_path)
        add_button.setFixedWidth(220)
        add_button.setStyleSheet(add_button.styleSheet().replace("text-align: center;", "text-align: left; padding-left: 35px;"))
        add_button.clicked.connect(self.add_note_action) # Renamed to avoid conflict

        key_icon_path = os.path.join(os.path.dirname(__file__), "assets", "KEY.png")
        secure_button = ModernButton(" Secure Note", primary=False, icon_path=key_icon_path)
        secure_button.setFixedWidth(220)
        secure_button.setStyleSheet(secure_button.styleSheet().replace("text-align: center;", "text-align: left; padding-left: 35px;"))
        secure_button.clicked.connect(self.add_secure_note_action) # Renamed

        actions_layout.addWidget(add_button)
        actions_layout.addWidget(secure_button)
        actions_layout.addStretch()
        layout.addLayout(actions_layout)
        return section

    def create_notes_section(self):
        section = QWidget()
        layout = QVBoxLayout(section)
        layout.setSpacing(20)
        header_layout = QHBoxLayout()
        title = QLabel("Your Notes")
        title.setStyleSheet("QLabel { color: #2c3e50; font-size: 24px; font-weight: bold; font-family: 'Arial', sans-serif; }")

        refresh_icon_path = os.path.join(os.path.dirname(__file__), "assets", "back.png")
        refresh_button = QPushButton(" Refresh")
        if os.path.exists(refresh_icon_path):
            refresh_icon = QIcon(refresh_icon_path)
            refresh_button.setIcon(refresh_icon)
            refresh_button.setIconSize(QSize(16, 16))

        refresh_button.setStyleSheet("""
            QPushButton {
                background: transparent; color: #667eea; border: none; font-size: 14px;
                font-weight: bold; padding: 5px 10px; text-align: left;
            }
            QPushButton:hover { background: rgba(102, 126, 234, 0.1); border-radius: 5px; }
        """)
        refresh_button.clicked.connect(self.load_notes)

        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(refresh_button)
        layout.addLayout(header_layout)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self.notes_container = QWidget()
        self.notes_layout = QGridLayout(self.notes_container)
        self.notes_layout.setSpacing(20)
        self.notes_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        scroll_area.setWidget(self.notes_container)
        layout.addWidget(scroll_area)
        return section

    def load_notes(self):
        for i in reversed(range(self.notes_layout.count())):
            child_item = self.notes_layout.itemAt(i)
            if child_item:
                widget = child_item.widget()
                if widget: widget.deleteLater()

        notes = self.note_service.get_notes_for_user(self.user.id)
        if not notes:
            empty_label = QLabel("No notes yet. Create your first note!")
            empty_label.setStyleSheet("QLabel { color: #7f8c8d; font-size: 16px; font-family: 'Arial', sans-serif; padding: 40px; text-align: center; }")
            empty_label.setAlignment(Qt.AlignCenter)
            self.notes_layout.addWidget(empty_label, 0, 0, 1, 4) # Span across 4 columns
            return

        row, col = 0, 0
        max_cols = 4 # Define how many cards per row
        for note_obj in notes:
            note_card = self.create_note_card(note_obj)
            self.notes_layout.addWidget(note_card, row, col)
            col = (col + 1) % max_cols
            if col == 0:
                row += 1
        # Add a stretch to push items to the top-left if not enough to fill last row
        if notes:
            self.notes_layout.setRowStretch(row + 1, 1)
            self.notes_layout.setColumnStretch(max_cols, 1)


    def create_note_card(self, note: Note):
        card = QFrame()
        card.setFixedSize(300, 150) # Or make it responsive
        card.setStyleSheet("""
            QFrame { background: white; border-radius: 15px; border: 1px solid rgba(0, 0, 0, 0.1); }
            QFrame:hover { background: #f8f9fa; border: 1px solid #667eea; }
        """)
        card.setCursor(Qt.PointingHandCursor)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 5)
        card.setGraphicsEffect(shadow)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(10)
        header_layout = QHBoxLayout()

        icon_label = QLabel()
        icon_base_style = "QLabel { font-size: 20px; color: #667eea; padding-right: 5px; }"
        if note.is_secure:
            key_icon_path = os.path.join(os.path.dirname(__file__), "assets", "KEY.png")
            if os.path.exists(key_icon_path):
                pixmap = QPixmap(key_icon_path).scaled(20, 20, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                icon_label.setPixmap(pixmap)
            else:
                icon_label.setText("🔒")
        else:
            note_icon_path = os.path.join(os.path.dirname(__file__), "assets", "note.png")
            if os.path.exists(note_icon_path):
                pixmap = QPixmap(note_icon_path).scaled(20, 20, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                icon_label.setPixmap(pixmap)
            else:
                icon_label.setText("📄")
        icon_label.setStyleSheet(icon_base_style)

        header_layout.addWidget(icon_label)
        header_layout.addStretch()

        delete_button = QPushButton()
        exit_icon_path = os.path.join(os.path.dirname(__file__), "assets", "exit.png")
        if os.path.exists(exit_icon_path):
            delete_icon = QIcon(exit_icon_path)
            delete_button.setIcon(delete_icon)
            delete_button.setIconSize(QSize(14, 14))
        else:
            delete_button.setText("🗑️")
        delete_button.setStyleSheet("""
            QPushButton { background: transparent; border: none; font-size: 14px; padding: 3px; }
            QPushButton:hover { background: rgba(231, 76, 60, 0.1); border-radius: 5px; }
        """)
        delete_button.setToolTip("Delete Note")
        delete_button.setFixedSize(24,24)
        delete_button.clicked.connect(lambda checked, n=note: self.delete_note_action(n)) # Renamed
        header_layout.addWidget(delete_button)
        layout.addLayout(header_layout)

        title_label = QLabel(note.note_name)
        title_label.setStyleSheet("QLabel { color: #2c3e50; font-size: 16px; font-weight: bold; font-family: 'Arial', sans-serif; }")
        title_label.setWordWrap(True)
        layout.addWidget(title_label)

        preview_text = (note.text_content[:80] + "..." if len(note.text_content or "") > 80 else note.text_content or "") or "Empty note"
        preview_label = QLabel(preview_text)
        preview_label.setStyleSheet("QLabel { color: #7f8c8d; font-size: 12px; font-family: 'Arial', sans-serif; }")
        preview_label.setWordWrap(True)
        preview_label.setFixedHeight(30)
        layout.addWidget(preview_label)
        layout.addStretch()
        card.mousePressEvent = lambda event, n=note: self.open_note_action(n) # Renamed
        return card

    def add_note_action(self):
        self.hide()
        from src.ui.add_note_window import AddNoteWindow # Delayed import
        self.add_note_window_instance = AddNoteWindow(self.user, self.note_service, self) # Pass note_service
        self.add_note_window_instance.show()

    def add_secure_note_action(self):
        password, ok = QInputDialog.getText(self, 'Secure Note Password',
                                          'Enter password (min 6 chars):', QLineEdit.Password)
        if ok and password:
            if len(password) < 6: # Basic validation
                QMessageBox.warning(self, "Password Too Short", "Password must be at least 6 characters.")
                return
            self.hide()
            from src.ui.add_note_window import AddNoteWindow # Delayed import
            self.add_note_window_instance = AddNoteWindow(self.user, self.note_service, self, secure_password_to_use=password)
            self.add_note_window_instance.show()

    def open_note_action(self, note: Note):
        if note.is_secure:
            password, ok = QInputDialog.getText(self, 'Enter Password',
                                              f'Password for "{note.note_name}":', QLineEdit.Password)
            if not ok: return
            if not password:
                QMessageBox.warning(self, "Password Required", "Password cannot be empty.")
                return

            # Use NoteService to verify password
            if not self.note_service.verify_secure_note_password(note, password):
                QMessageBox.warning(self, "Wrong Password", "Incorrect password!")
                return

        self.hide()
        from src.ui.note_window import NoteWindow # Delayed import
        # NoteWindow will need to be refactored to accept NoteService and UserFolderManager or similar
        self.note_window_instance = NoteWindow(self.user, note, self.note_service, self.user_folder_manager, home_window_ref=self)
        self.note_window_instance.show()

    def delete_note_action(self, note: Note):
        if QMessageBox.question(self, 'Delete Note', f'Are you sure you want to delete "{note.note_name}"?',
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No) == QMessageBox.Yes:
            try:
                self.note_service.delete_note(note.id, self.user.username) # Pass username for folder path
                self.load_notes()
                QMessageBox.information(self, "Note Deleted", f'Note "{note.note_name}" has been deleted.')
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not delete note: {e}")
                print(f"Error deleting note {note.id}: {e}")


    def sign_out(self):
        self.hide()
        # Need to import LoginWindow and pass UserService
        from src.ui.login_window import LoginWindow
        from src.services.user_service import UserService
        from src.data.user_repository import SQLiteUserRepository

        # Recreate UserService if needed, or pass the existing one if HomeWindow stored it.
        # For simplicity here, recreating. In a real app, you might pass it down or use a service locator.
        user_repository = SQLiteUserRepository()
        user_service = UserService(user_repository)

        self.login_window_instance = LoginWindow(user_service)
        self.login_window_instance.show()
        self.deleteLater()

    def close_application(self):
        if QMessageBox.question(self, 'Confirm Exit', "Exit NoteMaster?",
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No) == QMessageBox.Yes:
            QApplication.instance().quit()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.drag_position:
            self.move(event.globalPos() - self.drag_position)
            event.accept()

    def closeEvent(self, event): # This is Qt's close event, e.g. Alt+F4
        self.close_application()
        event.ignore() # Important to ignore if close_application handles quit


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Setup for testing - this would typically be done by main.py
    from src.data.database_manager import SQLiteDatabaseManager
    from src.data.user_repository import SQLiteUserRepository
    from src.services.user_service import UserService
    from src.data.note_repository import SQLiteNoteRepository


    db_manager = SQLiteDatabaseManager()
    user_repo = SQLiteUserRepository()
    user_service = UserService(user_repo)
    note_repo = SQLiteNoteRepository()
    note_service = NoteService(note_repo)

    try:
        test_user = user_service.register_user("hometest", "password123")
    except ValueError:
        test_user = user_service.authenticate_user("hometest", "password123")

    if not test_user:
        print("Failed to create/login test user for HomeWindow.")
        sys.exit(1)

    # Create a dummy note for testing display
    try:
        note_service.create_note(test_user.id, "My First Refactored Note", "This is a test.")
    except ValueError: # Note might already exist
        pass


    window = HomeWindow(test_user, note_service)
    window.show()
    sys.exit(app.exec_())