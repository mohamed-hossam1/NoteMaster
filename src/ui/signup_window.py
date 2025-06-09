import os
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QGraphicsDropShadowEffect,
    QLineEdit,  # Added QLineEdit
)
from PyQt5.QtCore import Qt, QPoint, QTimer
from PyQt5.QtGui import QFont, QPixmap, QColor

from src.ui.shared_ui_components import ModernButton, ModernLineEdit
from src.services.user_service import UserService
from src.ui.base_window import BaseWindow
from src.ui.styles import signup_window_styles as styles


class SignUpWindow(BaseWindow):
    def __init__(self, user_service: UserService):
        super().__init__(title="Sign Up - NoteMaster")
        self.user_service = user_service
        self.login_window_instance = None
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

        self.setStyleSheet(styles.SIGNUP_WINDOW_STYLE)

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

        assets_dir = os.path.join(os.path.dirname(__file__), "assets")
        note_icon_path = os.path.join(assets_dir, "note.png")

        app_icon_label = QLabel()
        if os.path.exists(note_icon_path):
            pixmap = QPixmap(note_icon_path)
            if pixmap.isNull():
                print(f"Warning: Could not load {note_icon_path}. Using fallback emoji.")
                app_icon_label.setText("📝")
                app_icon_label.setStyleSheet(styles.APP_ICON_LABEL_STYLE_EMOJI)
            else:
                scaled_pixmap = pixmap.scaled(
                    120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation
                )
                app_icon_label.setPixmap(scaled_pixmap)
                app_icon_label.setStyleSheet(styles.APP_ICON_LABEL_STYLE_IMAGE)
        else:
            # This print statement is the one you are seeing in the console
            print(f"Note: {os.path.join(os.path.dirname(__file__), 'assets', 'note.png')} not found. Using fallback emoji.")
            app_icon_label.setText("📝")
            app_icon_label.setStyleSheet(styles.APP_ICON_LABEL_STYLE_EMOJI)

        app_icon_label.setAlignment(Qt.AlignCenter)
        app_icon_label.setFixedSize(160, 160)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 10)
        app_icon_label.setGraphicsEffect(shadow)

        logo_layout.addWidget(app_icon_label)
        layout.addWidget(logo_container)
        return panel

    def _create_right_panel(self):
        panel = QFrame()
        panel.setStyleSheet(styles.RIGHT_PANEL_STYLE)

        layout = QVBoxLayout(panel)
        layout.setSpacing(20)
        layout.setContentsMargins(60, 35, 40, 40)

        close_button = QPushButton("×")
        close_button.setStyleSheet(styles.CLOSE_BUTTON_STYLE)
        close_button.setFixedSize(30, 30)
        close_button.clicked.connect(self.close_application)

        close_layout = QHBoxLayout()
        close_layout.addStretch()
        close_layout.addWidget(close_button)
        layout.addLayout(close_layout)

        welcome_label = QLabel("Create Account")
        welcome_label.setStyleSheet(styles.WELCOME_LABEL_STYLE)
        welcome_label.setAlignment(Qt.AlignCenter)

        subtitle_label = QLabel("Join NoteMaster today")
        subtitle_label.setStyleSheet(styles.SUBTITLE_LABEL_STYLE)
        subtitle_label.setAlignment(Qt.AlignCenter)

        layout.addWidget(welcome_label)
        layout.addWidget(subtitle_label)

        form_container = QWidget()
        form_layout = QVBoxLayout(form_container)
        form_layout.setSpacing(15)

        username_label = QLabel("Username")
        username_label.setStyleSheet(styles.FORM_LABEL_STYLE)
        self.username_field = ModernLineEdit("Choose a username")
        self.username_field.setStyleSheet(styles.TEXT_INPUT_STYLE)

        password_label = QLabel("Password")
        password_label.setStyleSheet(styles.FORM_LABEL_STYLE)
        self.password_field = ModernLineEdit("Create a password")
        self.password_field.setEchoMode(QLineEdit.Password) # This line caused the error
        self.password_field.setStyleSheet(styles.TEXT_INPUT_STYLE)

        confirm_label = QLabel("Confirm Password")
        confirm_label.setStyleSheet(styles.FORM_LABEL_STYLE)
        self.confirm_field = ModernLineEdit("Confirm your password")
        self.confirm_field.setEchoMode(QLineEdit.Password) # Also here
        self.confirm_field.setStyleSheet(styles.TEXT_INPUT_STYLE)

        form_layout.addWidget(username_label)
        form_layout.addWidget(self.username_field)
        form_layout.addWidget(password_label)
        form_layout.addWidget(self.password_field)
        form_layout.addWidget(confirm_label)
        form_layout.addWidget(self.confirm_field)

        layout.addWidget(form_container)

        self.signup_button = ModernButton("Create Account")
        self.signup_button.setFixedWidth(250)
        self.signup_button.clicked.connect(self.handle_signup)
        layout.addWidget(self.signup_button, alignment=Qt.AlignCenter)

        self.error_label = QLabel()
        self.error_label.setStyleSheet(styles.ERROR_LABEL_STYLE)
        self.error_label.setAlignment(Qt.AlignCenter)
        self.error_label.hide()
        layout.addWidget(self.error_label)

        login_container = QWidget()
        login_layout = QHBoxLayout(login_container)
        login_layout.setAlignment(Qt.AlignCenter)
        login_layout.setContentsMargins(0, 10, 0, 0)

        login_text = QLabel("Already have an account?")
        login_text.setStyleSheet(styles.LOGIN_TEXT_STYLE)

        login_button = QPushButton("Sign In")
        login_button.setStyleSheet(styles.LOGIN_BUTTON_STYLE)
        login_button.clicked.connect(self.handle_go_to_login)

        login_layout.addWidget(login_text)
        login_layout.addWidget(login_button)

        layout.addWidget(login_container)
        layout.addStretch()

        return panel

    def handle_signup(self):
        username = self.username_field.text().strip()
        password = self.password_field.text().strip()
        confirm_password = self.confirm_field.text().strip()

        if not username or not password or not confirm_password:
            self.show_error("Please fill in all fields!")
            return

        if password != confirm_password:
            self.show_error("Passwords do not match!")
            return

        try:
            self.user_service.register_user(username, password)
            self.show_error("Account created successfully! Redirecting to login...", success=True)
            QTimer.singleShot(2000, self.handle_go_to_login)
        except ValueError as e:
            self.show_error(str(e))

    def handle_go_to_login(self):
        self.hide()
        from src.ui.login_window import LoginWindow
        self.login_window_instance = LoginWindow(self.user_service)
        self.login_window_instance.show()
        self.deleteLater()

    def show_error(self, message, success=False):
        self.error_label.setText(message)
        if success:
            self.error_label.setStyleSheet("""
                QLabel {
                    color: #28a745;
                    font-size: 12px;
                    font-weight: bold;
                    background: rgba(40, 167, 69, 0.1);
                    padding: 10px;
                    border-radius: 5px;
                    border: 1px solid rgba(40, 167, 69, 0.3);
                }
            """)
        else:
            self.error_label.setStyleSheet(styles.ERROR_LABEL_STYLE)
        self.error_label.show()
        QTimer.singleShot(3000, self.error_label.hide)