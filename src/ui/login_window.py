import os
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QGraphicsDropShadowEffect,
    QPushButton,  # Added QPushButton
    QLineEdit,    # Added QLineEdit (though ModernLineEdit imports it, good for clarity if base used)
)
from PyQt5.QtCore import Qt, QPoint, QPropertyAnimation, QEasingCurve, QRect, QSize, QTimer
from PyQt5.QtGui import QFont, QPixmap, QPalette, QBrush, QColor, QPainter, QIcon

from src.ui.shared_ui_components import ModernButton, ModernLineEdit
from src.services.user_service import UserService
from src.ui.base_window import BaseWindow
from src.ui.styles import login_window_styles as styles


class LoginWindow(BaseWindow):
    def __init__(self, user_service: UserService):
        super().__init__(title="NoteMaster - Modern Note Taking")
        self.user_service = user_service
        self.home_window = None
        self.signup_window = None
        self.init_ui()

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        left_panel = self._create_left_panel()
        main_layout.addWidget(left_panel, 3)

        right_panel = self._create_right_panel()
        main_layout.addWidget(right_panel, 2)

        self.setStyleSheet(styles.LOGIN_WINDOW_STYLE)

    def _create_left_panel(self):
        panel = QFrame()
        panel.setStyleSheet(styles.LEFT_PANEL_STYLE)

        layout = QVBoxLayout(panel)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(30)

        logo_container = QWidget()
        logo_layout = QVBoxLayout(logo_container)
        logo_layout.setAlignment(Qt.AlignCenter)
        logo_layout.setSpacing(20)

        note_icon_path = os.path.join(os.path.dirname(__file__), "assets", "note.png")
        app_icon = QLabel()
        if os.path.exists(note_icon_path):
            pixmap = QPixmap(note_icon_path)
            scaled_pixmap = pixmap.scaled(
                120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            app_icon.setPixmap(scaled_pixmap)
            app_icon.setStyleSheet(styles.APP_ICON_LABEL_STYLE_IMAGE)
        else:
            app_icon.setText("📝")
            app_icon.setStyleSheet(styles.APP_ICON_LABEL_STYLE_EMOJI)

        app_icon.setAlignment(Qt.AlignCenter)
        app_icon.setFixedSize(160, 160)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 10)
        app_icon.setGraphicsEffect(shadow)

        logo_layout.addWidget(app_icon)
        layout.addWidget(logo_container)

        return panel

    def _create_right_panel(self):
        panel = QFrame()
        panel.setStyleSheet(styles.RIGHT_PANEL_STYLE)

        layout = QVBoxLayout(panel)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(25)
        layout.setContentsMargins(60, 35, 40, 60)

        close_button = QPushButton("×")
        close_button.setStyleSheet(styles.CLOSE_BUTTON_STYLE)
        close_button.setFixedSize(30, 30)
        close_button.clicked.connect(self.close_application)

        close_layout = QHBoxLayout()
        close_layout.addStretch()
        close_layout.addWidget(close_button)
        layout.addLayout(close_layout)

        welcome_label = QLabel("Welcome Back!")
        welcome_label.setStyleSheet(styles.WELCOME_LABEL_STYLE)
        welcome_label.setAlignment(Qt.AlignCenter)

        subtitle_label = QLabel("Sign in to continue to NoteMaster")
        subtitle_label.setStyleSheet(styles.SUBTITLE_LABEL_STYLE)
        subtitle_label.setAlignment(Qt.AlignCenter)

        layout.addWidget(welcome_label)
        layout.addWidget(subtitle_label)

        form_container = QWidget()
        form_layout = QVBoxLayout(form_container)
        form_layout.setSpacing(20)

        username_label = QLabel("Username")
        username_label.setStyleSheet(styles.FORM_LABEL_STYLE)
        self.username_field = ModernLineEdit("Enter your username")
        self.username_field.setStyleSheet(styles.TEXT_INPUT_STYLE)

        password_label = QLabel("Password")
        password_label.setStyleSheet(styles.FORM_LABEL_STYLE)
        self.password_field = ModernLineEdit("Enter your password")
        self.password_field.setEchoMode(QLineEdit.Password)
        self.password_field.setStyleSheet(styles.TEXT_INPUT_STYLE)

        form_layout.addWidget(username_label)
        form_layout.addWidget(self.username_field)
        form_layout.addWidget(password_label)
        form_layout.addWidget(self.password_field)

        layout.addWidget(form_container)

        self.login_button = ModernButton("Sign In")
        self.login_button.setFixedWidth(250)
        self.login_button.clicked.connect(self.handle_login)
        layout.addWidget(self.login_button, alignment=Qt.AlignCenter)

        self.error_label = QLabel()
        self.error_label.setStyleSheet(styles.ERROR_LABEL_STYLE)
        self.error_label.setAlignment(Qt.AlignCenter)
        self.error_label.hide()
        layout.addWidget(self.error_label)

        signup_container = QWidget()
        signup_layout = QHBoxLayout(signup_container)
        signup_layout.setAlignment(Qt.AlignCenter)

        signup_text = QLabel("Don\\'t have an account?")
        signup_text.setStyleSheet(styles.SIGNUP_TEXT_STYLE)

        signup_button = QPushButton("Sign Up")
        signup_button.setStyleSheet(styles.SIGNUP_BUTTON_STYLE)
        signup_button.clicked.connect(self.handle_go_to_signup)

        signup_layout.addWidget(signup_text)
        signup_layout.addWidget(signup_button)

        layout.addWidget(signup_container)
        layout.addStretch()

        return panel

    def handle_login(self):
        username = self.username_field.text().strip()
        password_entered = self.password_field.text().strip()

        if not username or not password_entered:
            self.show_error("Please fill in all fields!")
            return

        user = self.user_service.authenticate_user(username, password_entered)

        if user:
            self.hide()
            # Delayed import to avoid circular dependencies at module level
            from src.ui.home_window import HomeWindow # Corrected path
            from src.services.note_service import NoteService
            from src.data.note_repository import SQLiteNoteRepository
            # Ensure UserFolderManager is initialized if needed by HomeWindow or NoteService
            # For now, assuming User object passed to HomeWindow is sufficient.
            # If HomeWindow creates notes or NoteService needs user folder for new notes,
            # UserFolderManager might need to be instantiated.
            # User object should ideally carry its username for UserFolderManager.
            
            # Create note_service
            note_repository = SQLiteNoteRepository()
            note_service = NoteService(note_repository)

            self.home_window = HomeWindow(user, note_service)
            self.home_window.show()
            self.deleteLater()
        else:
            self.show_error("Invalid username or password!")

    def handle_go_to_signup(self):
        self.hide()
        from src.ui.signup_window import SignUpWindow
        self.signup_window = SignUpWindow(self.user_service)
        self.signup_window.show()
        self.deleteLater()

    def show_error(self, message):
        self.error_label.setText(message)
        self.error_label.show()
        QTimer.singleShot(3000, self.error_label.hide)