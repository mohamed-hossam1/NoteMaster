from PyQt5.QtWidgets import QPushButton, QLineEdit
from PyQt5.QtGui import QFont, QIcon # Added QIcon
from PyQt5.QtCore import Qt, QSize   # Added QSize


class ModernButton(QPushButton):
    def __init__(self, text, primary=True, icon_path=""): # Added icon_path parameter
        super().__init__(text)
        self.primary = primary
        self.setFixedHeight(45)
        self.setFont(QFont("Arial", 12, QFont.Bold))
        self.setCursor(Qt.PointingHandCursor)

        base_style_padding = "padding: 0 20px;"
        icon_style_qss = "" # For QSS specific icon styling if needed

        if icon_path and hasattr(self, 'setIcon'): # Check if setIcon method exists (it should for QPushButton)
            import os
            if os.path.exists(icon_path):
                qt_icon = QIcon(icon_path)
                self.setIcon(qt_icon)
                self.setIconSize(QSize(18, 18)) # Default icon size
                # Adjust padding if icon is present.
                # Qt handles icon placement, ensure text isn't too close.
                # This might need to be fine-tuned based on how text-align works with icons.
                base_style_padding = "padding-left: 15px; padding-right: 15px;"
                # icon_style_qss = "icon-size: 18px 18px;" # Can be added to common_style if needed
            else:
                print(f"Warning: Icon path not found: {icon_path}")

        common_style = f"""
            border-radius: 22px;
            font-size: 14px;
            font-weight: bold;
            text-align: center; /* Default to center, HomeWindow can override for left-aligned text with icon */
            {base_style_padding}
            {icon_style_qss}
        """

        if primary:
            self.setStyleSheet(
                f"""
                QPushButton {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #667eea, stop:1 #764ba2);
                    color: white;
                    border: none;
                    {common_style}
                }}
                QPushButton:hover {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #764ba2, stop:1 #667eea);
                }}
                QPushButton:pressed {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #5a67d8, stop:1 #6b46c1);
                }}
            """
            )
        else:
            self.setStyleSheet(
                f"""
                QPushButton {{
                    background: transparent;
                    color: #667eea;
                    border: 2px solid #667eea;
                    {common_style}
                }}
                QPushButton:hover {{
                    background: #667eea;
                    color: white;
                }}
            """
            )


class ModernLineEdit(QLineEdit):
    def __init__(self, placeholder=""):
        super().__init__()
        self.setPlaceholderText(placeholder)
        self.setFixedHeight(45)
        self.setFont(QFont("Arial", 12))
        # Style from login_window_styles.py (TEXT_INPUT_STYLE)
        # This was different in shared_ui_components.py previously.
        # Let's use the one from the login/signup styles for consistency if that was the intent
        # OR revert to the one that was in shared_ui_components if that was preferred.
        # For now, I'll use the one that seems to be applied in Login/Signup for visual consistency.
        self.setStyleSheet(
            """
            QLineEdit {
                background-color: #f8f9fa;
                border: 2px solid #e9ecef;
                color: #2c3e50; /* Adjusted for better visibility on light backgrounds if used elsewhere */
                font-size: 14px;
                padding: 0 15px;
                border-radius: 22px;
            }
            QLineEdit:focus {
                border: 2px solid #667eea;
                background-color: white;
            }
            QLineEdit::placeholder {
                color: #adb5bd; /* Placeholder for light backgrounds */
            }
        """
        )
        # If ModernLineEdit is always on a dark background like the original login/signup left panel,
        # then the original shared_ui_components.py style for ModernLineEdit might be better:
        # self.setStyleSheet(
        #     """
        #     QLineEdit {
        #         background-color: rgba(255, 255, 255, 0.1);
        #         border: 2px solid rgba(102, 126, 234, 0.3);
        #         color: white;
        #         font-size: 14px;
        #         padding: 0 15px;
        #         border-radius: 22px;
        #     }
        #     QLineEdit:focus {
        #         border: 2px solid #667eea;
        #         background-color: rgba(255, 255, 255, 0.15);
        #     }
        #     QLineEdit::placeholder {
        #         color: rgba(255, 255, 255, 0.7);
        #     }
        # """
        # )