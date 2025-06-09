from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtCore import Qt, QPoint


class BaseWindow(QMainWindow):
    def __init__(self, title="", fixed_size=(1200, 700)):
        super().__init__()
        self.setWindowTitle(title)
        self.setFixedSize(*fixed_size)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.drag_position = QPoint()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.drag_position:
            self.move(event.globalPos() - self.drag_position)
            event.accept()

    def close_application(self):
        QApplication.instance().quit()

    def closeEvent(self, event):
        self.close_application()
        event.accept()


