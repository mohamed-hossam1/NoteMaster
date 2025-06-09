SIGNUP_WINDOW_STYLE = """
QMainWindow {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #667eea, stop:0.5 #764ba2, stop:1 #f093fb);
}
"""

LEFT_PANEL_STYLE = """
QFrame {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(102, 126, 234, 0.8),
        stop:1 rgba(118, 75, 162, 0.8));
    border-radius: 0px;
}
"""

APP_ICON_LABEL_STYLE_IMAGE = """
QLabel {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 80px;
    padding: 20px;
}
"""

APP_ICON_LABEL_STYLE_EMOJI = """
QLabel {
    font-size: 120px;
    color: white;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 100px;
    padding: 40px;
}
"""

RIGHT_PANEL_STYLE = """
QFrame {
    background: rgba(255, 255, 255, 0.95);
    border-radius: 0px;
}
"""

CLOSE_BUTTON_STYLE = """
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
"""

WELCOME_LABEL_STYLE = """
QLabel {
    background: transparent;
    color: #2c3e50;
    font-size: 32px;
    font-weight: bold;
    font-family: 'Arial', sans-serif;
    margin-bottom: 5px;
}
"""

SUBTITLE_LABEL_STYLE = """
QLabel {
    background: transparent;
    color: #7f8c8d;
    font-size: 16px;
    font-family: 'Arial', sans-serif;
    margin-bottom: 20px;
}
"""

FORM_LABEL_STYLE = """
QLabel {
    background: transparent;
    color: #2c3e50;
    font-size: 14px;
    font-weight: bold;
    margin-bottom: 3px;
}
"""

TEXT_INPUT_STYLE = """
QLineEdit {
    background-color: #f8f9fa;
    border: 2px solid #e9ecef;
    color: #2c3e50;
    font-size: 14px;
    padding: 0 15px;
    border-radius: 22px;
}
QLineEdit:focus {
    border: 2px solid #667eea;
    background-color: white;
}
QLineEdit::placeholder {
    color: #adb5bd;
}
"""

ERROR_LABEL_STYLE = """
QLabel {
    color: #e74c3c;
    font-size: 12px;
    font-weight: bold;
    background: rgba(231, 76, 60, 0.1);
    padding: 10px;
    border-radius: 5px;
    border: 1px solid rgba(231, 76, 60, 0.3);
}
"""

LOGIN_TEXT_STYLE = """
QLabel {
    background: transparent;
    color: #7f8c8d;
    font-size: 14px;
}
"""

LOGIN_BUTTON_STYLE = """
QPushButton {
    background: transparent;
    color: #667eea;
    border: none;
    font-size: 14px;
    font-weight: bold;
    text-decoration: underline;
}
QPushButton:hover {
    color: #764ba2;
}
"""


