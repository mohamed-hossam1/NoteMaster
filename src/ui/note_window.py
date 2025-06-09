import sys
import os
import shutil
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QLineEdit, QPushButton,
                             QFrame, QGraphicsDropShadowEffect, QTabWidget,
                             QTextEdit, QColorDialog, QFileDialog, QMessageBox,
                             QSlider, QScrollArea, QGridLayout)
from PyQt5.QtCore import Qt, QPoint, QSize, QTimer, QBuffer, QIODevice
from PyQt5.QtGui import (QFont, QColor, QPainter, QPen, QPixmap, QImage,
                         QPainterPath, QBrush)

# Corrected imports for refactored structure
from src.core.interfaces import User, Note, SketchPoint, NoteImage, NoteAudio
from src.services.note_service import NoteService
from src.services.user_folder_manager import UserFolderManager
from src.ui.shared_ui_components import ModernButton

from typing import List # <--- IMPORT List HERE

import wave
import pyaudio 
import threading
import time

class CanvasWidget(QWidget):
    def __init__(self, note_id: int, note_service: NoteService, initial_points: List[SketchPoint]): # Added type hint for initial_points
        super().__init__()
        self.note_id = note_id
        self.note_service = note_service
        self.points = initial_points 
        self.newly_added_points = [] 

        self.drawing = False
        self.last_point = None
        self.brush_size = 5
        self.brush_color = QColor(0, 0, 0)
        self.setMinimumSize(800, 500)

        self.pixmap = QPixmap(self.size())
        self.pixmap.fill(Qt.white)

        self.redraw_from_db_points()

    def redraw_from_db_points(self):
        self.pixmap.fill(Qt.white)
        painter = QPainter(self.pixmap)
        painter.setRenderHint(QPainter.Antialiasing, True)

        # Draw existing points from DB as connected lines for each stroke
        # This simple version assumes points are ordered per stroke in the DB
        # A more robust solution would involve stroke IDs or saving segments.
        if not self.points:
            painter.end()
            self.update()
            return

        current_stroke_points_qt = []
        # It's tricky to perfectly reconstruct strokes without stroke IDs.
        # For now, let's try drawing lines between consecutive points if they have the same brush.
        # This is a simplification.
        
        last_pen_props = None

        for i in range(len(self.points)):
            point_data = self.points[i]
            current_qt_point = QPoint(int(point_data.x), int(point_data.y))
            
            pen = QPen()
            pen.setWidth(int(point_data.size))
            pen.setColor(QColor.fromRgbF(point_data.red, point_data.green, point_data.blue, point_data.opacity))
            pen.setCapStyle(Qt.RoundCap)
            pen.setJoinStyle(Qt.RoundJoin)
            
            painter.setPen(pen)

            if i > 0:
                # Basic heuristic: if brush properties are the same, assume it's a continued line
                prev_point_data = self.points[i-1]
                if (int(prev_point_data.size) == int(point_data.size) and
                    (prev_point_data.red, prev_point_data.green, prev_point_data.blue, prev_point_data.opacity) == \
                    (point_data.red, point_data.green, point_data.blue, point_data.opacity)):
                    prev_qt_point = QPoint(int(prev_point_data.x), int(prev_point_data.y))
                    painter.drawLine(prev_qt_point, current_qt_point)
                else: # Brush changed, start new point/stroke
                    painter.drawPoint(current_qt_point)
            else: # First point
                painter.drawPoint(current_qt_point)
        
        painter.end()
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self.pixmap)

    def resizeEvent(self, event):
        if self.pixmap.size() != self.size():
            new_pixmap = QPixmap(self.size())
            new_pixmap.fill(Qt.white)
            painter = QPainter(new_pixmap)
            painter.drawPixmap(0, 0, self.pixmap)
            painter.end()
            self.pixmap = new_pixmap
            self.redraw_from_db_points() 

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = True
            self.last_point = event.pos()

            point_data = SketchPoint(
                float(event.pos().x()), float(event.pos().y()),
                float(self.brush_size),
                self.brush_color.redF(), self.brush_color.greenF(),
                self.brush_color.blueF(), self.brush_color.alphaF()
            )
            self.newly_added_points.append(point_data)

            painter = QPainter(self.pixmap)
            painter.setRenderHint(QPainter.Antialiasing, True)
            pen = QPen(self.brush_color, self.brush_size, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
            painter.setPen(pen)
            painter.drawPoint(event.pos())
            painter.end()
            self.update()

    def mouseMoveEvent(self, event):
        if (event.buttons() & Qt.LeftButton) and self.drawing:
            point_data = SketchPoint(
                float(event.pos().x()), float(event.pos().y()),
                float(self.brush_size),
                self.brush_color.redF(), self.brush_color.greenF(),
                self.brush_color.blueF(), self.brush_color.alphaF()
            )
            self.newly_added_points.append(point_data)

            painter = QPainter(self.pixmap)
            painter.setRenderHint(QPainter.Antialiasing, True)
            pen = QPen(self.brush_color, self.brush_size, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
            painter.setPen(pen)
            painter.drawLine(self.last_point, event.pos())
            self.last_point = event.pos()
            painter.end()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.drawing:
            self.drawing = False
            if self.newly_added_points:
                for p_data in self.newly_added_points:
                    self.note_service.add_sketch_point_to_note(self.note_id, p_data)
                self.points.extend(self.newly_added_points) 
                self.newly_added_points = [] 


    def set_brush_size(self, size):
        self.brush_size = size

    def set_brush_color(self, color):
        self.brush_color = color

    def clear_canvas_content(self): 
        self.note_service.clear_sketch_points_for_note(self.note_id)
        self.points = [] 
        self.newly_added_points = []
        self.pixmap.fill(Qt.white)
        self.update()

    # This method was causing the NameError
    def get_all_points_for_saving(self) -> List[SketchPoint]:
        # This method might not be needed if points are saved per stroke/release
        return self.points


class ImageThumbnail(QLabel):
    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self.setFixedSize(150, 150)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("""
            QLabel {
                background: white; border: 1px solid #ddd; border-radius: 5px; padding: 5px;
            }
            QLabel:hover { border: 1px solid #667eea; }
        """)
        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            pixmap = pixmap.scaled(140, 140, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.setPixmap(pixmap)
        else:
            self.setText("Invalid Image")
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 50))
        shadow.setOffset(0, 3)
        self.setGraphicsEffect(shadow)


class AudioRecorder:
    def __init__(self, output_path):
        self.output_path = output_path
        self.is_recording = False
        self.frames = []
        self.audio_interface = pyaudio.PyAudio()
        self.stream = None
        self.thread = None

    def start_recording(self):
        if self.is_recording: return
        self.is_recording = True
        self.frames = []
        self.thread = threading.Thread(target=self._record)
        self.thread.daemon = True
        self.thread.start()

    def _record(self):
        try:
            self.stream = self.audio_interface.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)
            while self.is_recording:
                data = self.stream.read(1024, exception_on_overflow=False) 
                self.frames.append(data)
        except OSError as e:
            print(f"PyAudio OSError: {e}")
            QMessageBox.critical(None, "Audio Recording Error", f"Could not start recording: {e}")
            self.is_recording = False
        except Exception as e:
            print(f"Generic error during recording: {e}")
            self.is_recording = False
        finally:
            if self.stream:
                try:
                    if self.stream.is_active(): self.stream.stop_stream()
                    self.stream.close()
                except OSError: pass 
            self.stream = None
            # self.audio_interface.terminate() # Terminate only when completely done

    def stop_recording(self):
        if not self.is_recording and not self.frames:
             if self.audio_interface: self.audio_interface.terminate()
             return None

        self.is_recording = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.0)
        self.thread = None
        
        saved_path = None
        if self.frames:
            try:
                wf = wave.open(self.output_path, 'wb')
                wf.setnchannels(1)
                wf.setsampwidth(self.audio_interface.get_sample_size(pyaudio.paInt16))
                wf.setframerate(44100)
                wf.writeframes(b''.join(self.frames))
                wf.close()
                saved_path = self.output_path
            except Exception as e: print(f"Error saving audio: {e}")
        
        if self.audio_interface: 
            self.audio_interface.terminate()
        return saved_path


class AudioPlayer:
    def __init__(self, audio_path):
        self.audio_path = audio_path
        self.is_playing = False
        self.audio_interface = None 
        self.stream = None
        self.thread = None

    def play(self):
        if self.is_playing: return
        if not os.path.exists(self.audio_path):
            QMessageBox.warning(None, "Audio Playback Error", f"File not found: {os.path.basename(self.audio_path)}")
            return
        
        self.is_playing = True
        self.audio_interface = pyaudio.PyAudio() 
        self.thread = threading.Thread(target=self._play)
        self.thread.daemon = True
        self.thread.start()

    def _play(self):
        wf = None
        try:
            wf = wave.open(self.audio_path, 'rb')
            self.stream = self.audio_interface.open(
                format=self.audio_interface.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(), rate=wf.getframerate(), output=True)
            data = wf.readframes(1024)
            while data and self.is_playing:
                self.stream.write(data)
                data = wf.readframes(1024)
        except Exception as e: print(f"Error during playback: {e}")
        finally:
            if self.stream:
                try:
                    if self.stream.is_active(): self.stream.stop_stream()
                    self.stream.close()
                except OSError: pass
            if wf: wf.close()
            self.is_playing = False
            if self.audio_interface: self.audio_interface.terminate() 

    def stop(self):
        self.is_playing = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.0)
        self.thread = None


class NoteWindow(QMainWindow): 
    def __init__(self, user: User, note: Note, note_service: NoteService, user_folder_manager: UserFolderManager, home_window_ref=None):
        super().__init__()
        self.user = user
        self.note = note 
        self.note_service = note_service
        self.user_folder_manager = user_folder_manager
        self.home_window_ref = home_window_ref

        self.setWindowTitle(f"NoteMaster - {note.note_name}")
        self.setFixedSize(1200, 800)
        self.setWindowFlags(Qt.FramelessWindowHint)

        self.drag_position = QPoint()
        self.audio_recorder = None
        self.audio_player = None

        self.init_ui()
        self.load_note_data()

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        header = self.create_header()
        main_layout.addWidget(header)
        content_area = self.create_content_area()
        main_layout.addWidget(content_area)

        self.setStyleSheet("QMainWindow { background: white; }")

    def create_header(self):
        header = QFrame()
        header.setFixedHeight(80)
        header.setStyleSheet("""
            QFrame { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #667eea, stop:1 #764ba2);
                     border-bottom: 1px solid rgba(0, 0, 0, 0.1); }
        """)
        layout = QHBoxLayout(header)
        layout.setContentsMargins(30, 0, 30, 0)
        title_label = QLabel(self.note.note_name)
        title_label.setStyleSheet("QLabel { background: transparent; color: white; font-size: 24px; font-weight: bold; font-family: 'Arial'; }")
        close_button = QPushButton("×")
        close_button.setStyleSheet("""
            QPushButton { background: rgba(255,255,255,0.2); color: white; border: none; font-size: 24px; font-weight: bold; padding: 5px; border-radius: 15px; }
            QPushButton:hover { background: rgba(255,255,255,0.3); }
        """)
        close_button.setFixedSize(30, 30)
        close_button.clicked.connect(self.handle_save_and_close)
        back_button = QPushButton("← Back")
        back_button.setStyleSheet(close_button.styleSheet().replace("font-size: 24px;", "font-size: 14px; padding: 8px 15px; border-radius: 5px;")) 
        back_button.clicked.connect(self.handle_save_and_close)
        layout.addWidget(back_button)
        layout.addStretch()
        layout.addWidget(title_label)
        layout.addStretch()
        layout.addWidget(close_button)
        return header

    def create_content_area(self):
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #ddd; background: white; border-radius: 5px; }
            QTabBar::tab { background: #f8f9fa; color: #495057; padding: 10px 20px; border: 1px solid #ddd; 
                           border-bottom: none; border-top-left-radius: 5px; border-top-right-radius: 5px; 
                           min-width: 100px; font-size: 14px; font-weight: bold; }
            QTabBar::tab:selected { background: white; color: #667eea; border-bottom: 3px solid #667eea; }
            QTabBar::tab:hover { background: #e9ecef; }
        """)
        self.setup_tabs()
        layout.addWidget(self.tab_widget)
        save_button = ModernButton("Save Note")
        save_button.setFixedWidth(200)
        save_button.clicked.connect(self.handle_save_note)
        layout.addWidget(save_button, alignment=Qt.AlignCenter)
        return content

    def setup_tabs(self):
        self.create_text_tab()
        self.create_drawing_tab()
        self.create_images_tab()
        self.create_audio_tab()

    def load_note_data(self):
        # Reload note from DB to get freshest data, including media lists
        updated_note = self.note_service._get_note_by_id(self.note.id, self.user.id) # Use the helper if available
        if updated_note:
            self.note = updated_note # Update local note object

        self.text_editor.setText(self.note.text_content or "")
        self.canvas.points = self.note.sketch_points # Update canvas points
        self.canvas.redraw_from_db_points()
        self.refresh_images_display()
        self.refresh_audio_display()


    def create_text_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        self.text_editor = QTextEdit()
        self.text_editor.setStyleSheet("""
            QTextEdit { background: white; border: 1px solid #ddd; border-radius: 5px; 
                        padding: 10px; font-size: 14px; color: #2c3e50; }
        """)
        self.text_editor.setPlaceholderText("Start typing your note here...")
        layout.addWidget(self.text_editor)
        self.tab_widget.addTab(tab, "Text")

    def create_drawing_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20,20,20,20)
        controls_layout = QHBoxLayout()
        color_button = QPushButton("Choose Color")
        color_button.setStyleSheet("QPushButton { background: #f8f9fa; color: #495057; border: 1px solid #ddd; border-radius: 5px; padding: 8px 15px; font-size: 14px;} QPushButton:hover { background: #e9ecef; }")
        color_button.clicked.connect(self.choose_draw_color)
        size_label = QLabel("Brush Size:")
        size_label.setStyleSheet("QLabel { color: #495057; font-size: 14px; }")
        self.size_slider = QSlider(Qt.Horizontal)
        self.size_slider.setMinimum(1); self.size_slider.setMaximum(30); self.size_slider.setValue(5)
        self.size_slider.setStyleSheet("QSlider::groove:horizontal { height: 8px; background: #f8f9fa; border: 1px solid #ddd; border-radius: 4px; } QSlider::handle:horizontal { background: #667eea; border: 1px solid #5a67d8; width: 18px; margin: -6px 0; border-radius: 9px; }")
        self.size_slider.valueChanged.connect(self.update_draw_brush_size)
        clear_button = QPushButton("Clear Canvas")
        clear_button.setStyleSheet(color_button.styleSheet())
        clear_button.clicked.connect(self.confirm_clear_canvas)
        controls_layout.addWidget(color_button); controls_layout.addWidget(size_label); controls_layout.addWidget(self.size_slider); controls_layout.addWidget(clear_button)
        layout.addLayout(controls_layout)
        canvas_scroll = QScrollArea(); canvas_scroll.setWidgetResizable(True)
        canvas_scroll.setStyleSheet("QScrollArea { border: 1px solid #ddd; border-radius: 5px; background: white; }")
        self.canvas = CanvasWidget(self.note.id, self.note_service, self.note.sketch_points)
        canvas_scroll.setWidget(self.canvas)
        layout.addWidget(canvas_scroll)
        self.tab_widget.addTab(tab, "Drawing")

    def create_images_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20,20,20,20)
        controls_layout = QHBoxLayout()
        add_image_button = QPushButton("Add Image")
        add_image_button.setStyleSheet("QPushButton { background: #f8f9fa; color: #495057; border: 1px solid #ddd; border-radius: 5px; padding: 8px 15px; font-size: 14px; } QPushButton:hover { background: #e9ecef; }")
        add_image_button.clicked.connect(self.handle_add_image)
        controls_layout.addWidget(add_image_button); controls_layout.addStretch()
        layout.addLayout(controls_layout)
        scroll_area = QScrollArea(); scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: 1px solid #ddd; border-radius: 5px; background: white; }")
        self.images_container = QWidget()
        self.images_layout = QGridLayout(self.images_container)
        self.images_layout.setSpacing(10)
        scroll_area.setWidget(self.images_container)
        layout.addWidget(scroll_area)
        self.tab_widget.addTab(tab, "Images")

    def create_audio_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20,20,20,20)
        controls_layout = QHBoxLayout()
        self.record_button = QPushButton("🎙️ Start Recording")
        self.record_button.setStyleSheet("QPushButton { background: #f8f9fa; color: #495057; border: 1px solid #ddd; border-radius: 5px; padding: 8px 15px; font-size: 14px; } QPushButton:hover { background: #e9ecef; }")
        self.record_button.clicked.connect(self.toggle_audio_recording)
        controls_layout.addWidget(self.record_button); controls_layout.addStretch()
        layout.addLayout(controls_layout)
        self.audio_list_widget = QWidget()
        self.audio_list_layout = QVBoxLayout(self.audio_list_widget)
        self.audio_list_layout.setAlignment(Qt.AlignTop)
        scroll_area = QScrollArea(); scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: 1px solid #ddd; border-radius: 5px; background: white; }")
        scroll_area.setWidget(self.audio_list_widget)
        layout.addWidget(scroll_area)
        self.tab_widget.addTab(tab, "Audio")

    def refresh_images_display(self):
        for i in reversed(range(self.images_layout.count())):
            widget = self.images_layout.itemAt(i).widget()
            if widget: widget.deleteLater()
        row, col, max_cols = 0,0,4
        for image_obj in self.note.image_paths: 
            thumbnail = ImageThumbnail(image_obj.image_path) 
            container = QWidget(); container_layout = QVBoxLayout(container); container_layout.setSpacing(5)
            name_label = QLabel(os.path.basename(image_obj.image_path)) 
            name_label.setStyleSheet("QLabel { color: #495057; font-size: 12px; text-align: center; }")
            name_label.setAlignment(Qt.AlignCenter); name_label.setWordWrap(True)
            delete_btn_style = "QPushButton { background: #f8f9fa; color: #e74c3c; border: 1px solid #ddd; border-radius: 5px; padding: 5px; font-size: 12px; } QPushButton:hover { background: rgba(231,76,60,0.1); border: 1px solid #e74c3c; }"
            delete_button = QPushButton("Delete"); delete_button.setStyleSheet(delete_btn_style)
            delete_button.clicked.connect(lambda checked, path=image_obj.image_path: self.confirm_delete_image(path))
            container_layout.addWidget(thumbnail); container_layout.addWidget(name_label); container_layout.addWidget(delete_button)
            self.images_layout.addWidget(container, row, col)
            col = (col + 1) % max_cols
            if col == 0: row += 1

    def refresh_audio_display(self):
        for i in reversed(range(self.audio_list_layout.count())):
            widget = self.audio_list_layout.itemAt(i).widget()
            if widget: widget.deleteLater()
        for audio_obj in self.note.audio_paths: 
            item_widget = QWidget(); item_layout = QHBoxLayout(item_widget)
            name_label = QLabel(os.path.basename(audio_obj.audio_path)) 
            name_label.setStyleSheet("QLabel { color: #495057; font-size: 14px; }")
            btn_style_base = "QPushButton {{ background: #f8f9fa; color: {color}; border: 1px solid #ddd; border-radius: 5px; padding: 5px 10px; font-size: 12px; }} QPushButton:hover {{ background: {hover_bg}; {hover_border} }}"
            play_button = QPushButton("▶️ Play")
            play_button.setStyleSheet(btn_style_base.format(color="#495057", hover_bg="#e9ecef", hover_border=""))
            play_button.clicked.connect(lambda checked, path=audio_obj.audio_path: self.play_audio_file(path))
            delete_button = QPushButton("🗑️ Delete")
            delete_button.setStyleSheet(btn_style_base.format(color="#e74c3c", hover_bg="rgba(231,76,60,0.1)", hover_border="border: 1px solid #e74c3c;"))
            delete_button.clicked.connect(lambda checked, path=audio_obj.audio_path: self.confirm_delete_audio(path))
            item_layout.addWidget(name_label); item_layout.addStretch(); item_layout.addWidget(play_button); item_layout.addWidget(delete_button)
            self.audio_list_layout.addWidget(item_widget)

    def choose_draw_color(self):
        color = QColorDialog.getColor()
        if color.isValid(): self.canvas.set_brush_color(color)

    def update_draw_brush_size(self, size): self.canvas.set_brush_size(size)

    def confirm_clear_canvas(self):
        if QMessageBox.question(self, 'Clear Canvas', 'Are you sure?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No) == QMessageBox.Yes:
            self.canvas.clear_canvas_content()

    def handle_add_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Add Image", "", "Images (*.png *.jpg *.jpeg *.bmp *.gif)")
        if file_path:
            images_dir = self.user_folder_manager.get_images_path() 
            os.makedirs(images_dir, exist_ok=True)
            dest_filename = os.path.basename(file_path)
            dest_path = os.path.join(images_dir, dest_filename)
            count = 1
            name, ext = os.path.splitext(dest_filename)
            while os.path.exists(dest_path):
                dest_filename = f"{name}_{count}{ext}"
                dest_path = os.path.join(images_dir, dest_filename)
                count += 1
            try:
                shutil.copy2(file_path, dest_path)
                self.note_service.add_image_to_note(self.note.id, dest_path)
                # self.note.image_paths.append(NoteImage(dest_path)) # Service should handle truth, reload data
                self.load_note_data() # Reload to get updated image list
            except Exception as e: QMessageBox.critical(self, "Error", f"Could not copy image: {e}")

    def confirm_delete_image(self, image_path_to_delete):
        if QMessageBox.question(self, 'Delete Image', 'Are you sure?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No) == QMessageBox.Yes:
            try:
                self.note_service.remove_image_from_note(self.note.id, image_path_to_delete)
                if os.path.exists(image_path_to_delete): os.remove(image_path_to_delete)
                # self.note.image_paths = [img for img in self.note.image_paths if img.image_path != image_path_to_delete]
                self.load_note_data() # Reload
            except Exception as e: QMessageBox.warning(self, "Error", f"Could not delete image: {e}")

    def toggle_audio_recording(self):
        if self.audio_recorder and self.audio_recorder.is_recording:
            output_path = self.audio_recorder.stop_recording()
            self.audio_recorder = None
            if output_path:
                self.note_service.add_audio_to_note(self.note.id, output_path)
                # self.note.audio_paths.append(NoteAudio(output_path)) 
                self.load_note_data() # Reload
            self.record_button.setText("🎙️ Start Recording")
            self.record_button.setStyleSheet("QPushButton { background: #f8f9fa; color: #495057; border: 1px solid #ddd; border-radius: 5px; padding: 8px 15px; font-size: 14px; } QPushButton:hover { background: #e9ecef; }")
        else:
            if self.audio_player and self.audio_player.is_playing: self.audio_player.stop()
            if self.audio_recorder : 
                if self.audio_recorder.audio_interface: self.audio_recorder.audio_interface.terminate()

            audio_dir = self.user_folder_manager.get_audio_path()
            os.makedirs(audio_dir, exist_ok=True)
            filename = f"audio_{int(time.time())}.wav"
            output_path = os.path.join(audio_dir, filename)
            self.audio_recorder = AudioRecorder(output_path)
            self.audio_recorder.start_recording()
            QTimer.singleShot(200, self._update_record_button_on_status_change)


    def _update_record_button_on_status_change(self):
        if self.audio_recorder and self.audio_recorder.is_recording:
            self.record_button.setText("🛑 Stop Recording")
            self.record_button.setStyleSheet("QPushButton { background: rgba(231,76,60,0.1); color: #e74c3c; border: 1px solid #e74c3c; border-radius: 5px; padding: 8px 15px; font-size: 14px; } QPushButton:hover { background: rgba(231,76,60,0.2); }")
        else: 
            self.record_button.setText("🎙️ Start Recording")
            self.record_button.setStyleSheet("QPushButton { background: #f8f9fa; color: #495057; border: 1px solid #ddd; border-radius: 5px; padding: 8px 15px; font-size: 14px; } QPushButton:hover { background: #e9ecef; }")
            if self.audio_recorder : 
                if self.audio_recorder.audio_interface : self.audio_recorder.audio_interface.terminate()
                self.audio_recorder = None


    def play_audio_file(self, audio_path):
        if self.audio_player and self.audio_player.is_playing: self.audio_player.stop()
        if self.audio_recorder and self.audio_recorder.is_recording: self.toggle_audio_recording()
        elif self.audio_recorder:
            if self.audio_recorder.audio_interface: self.audio_recorder.audio_interface.terminate()
            self.audio_recorder = None

        self.audio_player = AudioPlayer(audio_path)
        self.audio_player.play()

    def confirm_delete_audio(self, audio_path_to_delete):
        if QMessageBox.question(self, 'Delete Audio', 'Are you sure?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No) == QMessageBox.Yes:
            if self.audio_player and self.audio_player.audio_path == audio_path_to_delete and self.audio_player.is_playing:
                self.audio_player.stop()
                self.audio_player = None
            try:
                self.note_service.remove_audio_from_note(self.note.id, audio_path_to_delete) 
                if os.path.exists(audio_path_to_delete): os.remove(audio_path_to_delete)
                # self.note.audio_paths = [aud for aud in self.note.audio_paths if aud.audio_path != audio_path_to_delete]
                self.load_note_data() # Reload
            except Exception as e: QMessageBox.warning(self, "Error", f"Could not delete audio: {e}")


    def handle_save_note(self):
        self.note.text_content = self.text_editor.toPlainText()
        self.note_service.update_note_content(self.note.id, self.note.text_content)
        QMessageBox.information(self, "Note Saved", "Note saved successfully!")

    def _cleanup_media_resources_on_close(self):
        if self.audio_recorder:
            if self.audio_recorder.is_recording: self.audio_recorder.stop_recording()
            elif self.audio_recorder.audio_interface: self.audio_recorder.audio_interface.terminate()
            self.audio_recorder = None
        if self.audio_player:
            if self.audio_player.is_playing: self.audio_player.stop()
            elif self.audio_player.audio_interface: self.audio_player.audio_interface.terminate()
            self.audio_player = None

    def handle_save_and_close(self):
        self.handle_save_note()
        self._cleanup_media_resources_on_close()
        self.hide()
        if self.home_window_ref:
            self.home_window_ref.load_notes()
            self.home_window_ref.show()
        self.deleteLater()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.drag_position:
            self.move(event.globalPos() - self.drag_position)
            event.accept()

    def closeEvent(self, event): 
        self.handle_save_note()
        self._cleanup_media_resources_on_close()
        if self.home_window_ref and not self.home_window_ref.isVisible():
             self.home_window_ref.load_notes()
             self.home_window_ref.show()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    from src.data.database_manager import SQLiteDatabaseManager
    from src.data.user_repository import SQLiteUserRepository
    from src.services.user_service import UserService # Added import
    from src.data.note_repository import SQLiteNoteRepository
    from src.ui.home_window import HomeWindow


    db_m = SQLiteDatabaseManager() 
    user_r = SQLiteUserRepository()
    note_r = SQLiteNoteRepository()

    user_s = UserService(user_r) 
    note_s = NoteService(note_r)
    
    try:
        current_user = user_s.register_user("notewinuser", "testpass")
    except ValueError:
        current_user = user_s.authenticate_user("notewinuser", "testpass")

    if not current_user:
        print("Could not get/create user for NoteWindow test.")
        sys.exit(1)

    user_fm = UserFolderManager(current_user.username)

    test_note_obj = None
    # Ensure user notes are fetched using the correct user id
    user_notes = note_s.get_notes_for_user(current_user.id) 
    if not user_notes:
        try:
            test_note_obj = note_s.create_note(current_user.id, "Test Note for Window")
        except ValueError: 
             pass 
    else:
        test_note_obj = user_notes[0]
    
    if not test_note_obj: 
        user_notes = note_s.get_notes_for_user(current_user.id)
        if user_notes: test_note_obj = user_notes[0]
        else:
            print("Could not create or get a note for testing.")
            sys.exit(1)

    class DummyHome(QMainWindow):
        def __init__(self, usr, ns):
            super().__init__()
            self.user = usr
            self.note_service = ns 
            self.label = QLabel("Dummy Home Window")
            self.setCentralWidget(self.label)
        def load_notes(self): print("DummyHome: load_notes called")
        def show(self):
            print("DummyHome: show called")
            super().show()

    dummy_home_ref = DummyHome(current_user, note_s)

    window = NoteWindow(current_user, test_note_obj, note_s, user_fm, home_window_ref=dummy_home_ref)
    window.show()
    
    exit_code = app.exec_()
    sys.exit(exit_code)