"""
Main Student Study Kit Application
A comprehensive PyQt6 application for students
"""

import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QTextEdit, QComboBox, QSpinBox,
    QDateTimeEdit, QTableWidget, QTableWidgetItem, QListWidget, QListWidgetItem,
    QStackedWidget, QFrame, QScrollArea, QFileDialog, QMessageBox, QDialog,
    QFormLayout, QGridLayout, QProgressBar, QCheckBox, QSlider, QTabWidget,
    QSplitter, QGroupBox, QCalendarWidget, QTimeEdit, QColorDialog, QMenu,
    QSystemTrayIcon, QMenuBar, QStatusBar, QToolBar, QSizePolicy, QSpacerItem,
    QInputDialog
)
from PyQt6.QtCore import (
    Qt, QTimer, QTime, QDate, QDateTime, pyqtSignal, QSize, QUrl, QPropertyAnimation,
    QEasingCurve, QPoint, QRect
)
from PyQt6.QtGui import (
    QIcon, QFont, QPixmap, QColor, QPalette, QLinearGradient, QBrush,
    QKeySequence, QAction, QCursor, QFontDatabase, QImage, QDesktopServices
)
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtPdfWidgets import QPdfView
from PyQt6.QtPdf import QPdfDocument

from database import DatabaseManager
from sound_manager import SoundManager
from audio_recorder import AudioRecorder
from language_manager import LanguageManager, get_language_manager, _

# Initialize language manager globally
lang_mgr = get_language_manager()


# Modern color scheme
COLORS = {
    'primary': '#6366f1',
    'primary_dark': '#4f46e5',
    'secondary': '#ec4899',
    'accent': '#8b5cf6',
    'success': '#22c55e',
    'warning': '#f59e0b',
    'danger': '#ef4444',
    'info': '#3b82f6',
    'bg_dark': '#0f172a',
    'bg_card': '#1e293b',
    'bg_hover': '#334155',
    'text_primary': '#f8fafc',
    'text_secondary': '#94a3b8',
    'text_muted': '#64748b',
    'border': '#334155'
}


class ModernButton(QPushButton):
    """Modern styled button with sound effects"""
    def __init__(self, text, variant='primary', icon=None, parent=None):
        super().__init__(text, parent)
        self.variant = variant
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setMinimumHeight(40)
        self.apply_style()
    
    def apply_style(self):
        if self.variant == 'primary':
            self.setStyleSheet(f'''
                QPushButton {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                        stop:0 {COLORS['primary']}, stop:1 {COLORS['accent']});
                    color: white;
                    border: none;
                    border-radius: 10px;
                    padding: 10px 20px;
                    font-weight: 600;
                    font-size: 13px;
                }}
                QPushButton:hover {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 {COLORS['primary_dark']}, stop:1 {COLORS['accent']});
                }}
                QPushButton:pressed {{
                    background: {COLORS['primary_dark']};
                }}
            ''')
        elif self.variant == 'secondary':
            self.setStyleSheet(f'''
                QPushButton {{
                    background: {COLORS['bg_card']};
                    color: {COLORS['text_primary']};
                    border: 2px solid {COLORS['border']};
                    border-radius: 10px;
                    padding: 10px 20px;
                    font-weight: 600;
                    font-size: 13px;
                }}
                QPushButton:hover {{
                    background: {COLORS['bg_hover']};
                    border-color: {COLORS['primary']};
                }}
            ''')
        elif self.variant == 'danger':
            self.setStyleSheet(f'''
                QPushButton {{
                    background: {COLORS['danger']};
                    color: white;
                    border: none;
                    border-radius: 10px;
                    padding: 10px 20px;
                    font-weight: 600;
                    font-size: 13px;
                }}
                QPushButton:hover {{
                    background: #dc2626;
                }}
            ''')
        elif self.variant == 'success':
            self.setStyleSheet(f'''
                QPushButton {{
                    background: {COLORS['success']};
                    color: white;
                    border: none;
                    border-radius: 10px;
                    padding: 10px 20px;
                    font-weight: 600;
                    font-size: 13px;
                }}
                QPushButton:hover {{
                    background: #16a34a;
                }}
            ''')


class CardFrame(QFrame):
    """Modern card container"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f'''
            QFrame {{
                background-color: {COLORS['bg_card']};
                border-radius: 16px;
                border: 1px solid {COLORS['border']};
            }}
        ''')


class PomodoroWidget(QWidget):
    """Pomodoro Zamanlayıcı Widget'ı"""
    def __init__(self, db, sound_manager, parent=None):
        super().__init__(parent)
        self.db = db
        self.sound = sound_manager
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        
        self.time_left = 25 * 60  # 25 minutes
        self.original_time = 25 * 60
        self.is_running = False
        self.is_break = False
        self.current_subject = ""
        
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        self.title_label = QLabel(_('pomodoro.title'))
        self.title_label.setStyleSheet(f'''
            font-size: 32px;
            font-weight: 700;
            color: {COLORS['text_primary']};
        ''')
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label)
        
        # Stats cards
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(15)
        
        self.stats_labels = {}
        self.stat_keys = [
            ('pomodoro.stats.todays_sessions', 'Bugünkü Seanslar'),
            ('pomodoro.stats.focus_duration', 'Odak Süresi'),
            ('pomodoro.stats.completed', 'Tamamlanan')
        ]
        
        for key, default_text in self.stat_keys:
            card = CardFrame()
            card_layout = QVBoxLayout(card)
            card_layout.setSpacing(5)
            card_layout.setContentsMargins(20, 20, 20, 20)
            
            lbl = QLabel(_(key, default_text))
            lbl.setStyleSheet(f'color: {COLORS["text_secondary"]}; font-size: 12px;')
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            val = QLabel('0')
            val.setStyleSheet(f'color: {COLORS["text_primary"]}; font-size: 24px; font-weight: 700;')
            val.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            self.stats_labels[key] = (lbl, val)
            
            card_layout.addWidget(lbl)
            card_layout.addWidget(val)
            stats_layout.addWidget(card)
        
        layout.addLayout(stats_layout)
        
        # Timer display
        timer_card = CardFrame()
        timer_layout = QVBoxLayout(timer_card)
        timer_layout.setSpacing(20)
        timer_layout.setContentsMargins(40, 40, 40, 40)
        
        self.timer_label = QLabel('25:00')
        self.timer_label.setStyleSheet(f'''
            font-size: 96px;
            font-weight: 200;
            color: {COLORS['primary']};
        ''')
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        timer_layout.addWidget(self.timer_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(100)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(8)
        self.progress_bar.setStyleSheet(f'''
            QProgressBar {{
                background-color: {COLORS['bg_dark']};
                border-radius: 4px;
            }}
            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {COLORS['primary']}, stop:1 {COLORS['accent']});
                border-radius: 4px;
            }}
        ''')
        timer_layout.addWidget(self.progress_bar)
        
        # Mode indicator
        self.mode_label = QLabel(_('pomodoro.timer.focus_time'))
        self.mode_label.setStyleSheet(f'''
            color: {COLORS['success']};
            font-size: 14px;
            font-weight: 600;
            letter-spacing: 2px;
        ''')
        self.mode_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        timer_layout.addWidget(self.mode_label)
        
        layout.addWidget(timer_card)
        
        # Subject selector
        subject_layout = QHBoxLayout()
        self.subject_label = QLabel(_('pomodoro.subject') + ':')
        self.subject_label.setStyleSheet(f'color: {COLORS["text_secondary"]};')
        subject_layout.addWidget(self.subject_label)
        subject_layout.addStretch()
        
        self.subject_combo = QComboBox()
        self.subject_combo.setEditable(True)
        self.subject_combo.addItems(lang_mgr.translations.get(lang_mgr.current_language, {}).get('pomodoro', {}).get('subjects', []))
        self.subject_combo.setStyleSheet(f'''
            QComboBox {{
                background-color: {COLORS['bg_card']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 8px 12px;
                min-width: 200px;
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QComboBox QAbstractItemView {{
                background-color: {COLORS['bg_card']};
                color: {COLORS['text_primary']};
                selection-background-color: {COLORS['primary']};
            }}
        ''')
        self.subject_combo.currentTextChanged.connect(self.set_subject)
        subject_layout.addWidget(self.subject_combo)
        subject_layout.addStretch()
        
        layout.addLayout(subject_layout)
        
        # Controls
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(15)
        
        self.start_btn = ModernButton(_('pomodoro.controls.start'), 'success')
        self.start_btn.clicked.connect(self.start_timer)
        controls_layout.addWidget(self.start_btn)
        
        self.pause_btn = ModernButton(_('pomodoro.controls.pause'), 'secondary')
        self.pause_btn.clicked.connect(self.pause_timer)
        self.pause_btn.setEnabled(False)
        controls_layout.addWidget(self.pause_btn)
        
        self.reset_btn = ModernButton(_('pomodoro.controls.reset'), 'secondary')
        self.reset_btn.clicked.connect(self.reset_timer)
        controls_layout.addWidget(self.reset_btn)
        
        layout.addLayout(controls_layout)
        
        # Duration presets
        presets_layout = QHBoxLayout()
        presets_layout.setSpacing(10)
        
        self.duration_presets_label = QLabel(_('pomodoro.duration') + ':')
        self.duration_presets_label.setStyleSheet(f'color: {COLORS["text_secondary"]};')
        presets_layout.addWidget(self.duration_presets_label)
        
        self.duration_btns = []
        for minutes, label_key in [(15, 'pomodoro.durations.15m'), (25, 'pomodoro.durations.25m'), 
                                    (45, 'pomodoro.durations.45m'), (60, 'pomodoro.durations.60m')]:
            btn = ModernButton(_(label_key), 'secondary')
            btn.setFixedWidth(80)
            btn.clicked.connect(lambda checked, m=minutes: self.set_duration(m))
            presets_layout.addWidget(btn)
            self.duration_btns.append((btn, label_key))
        
        presets_layout.addStretch()
        layout.addLayout(presets_layout)
        
        # Break toggle
        self.break_check = QCheckBox(_('pomodoro.break.short_break'))
        self.break_check.setStyleSheet(f'''
            QCheckBox {{
                color: {COLORS['text_secondary']};
                font-size: 13px;
            }}
            QCheckBox::indicator {{
                width: 20px;
                height: 20px;
                border-radius: 4px;
                border: 2px solid {COLORS['border']};
                background-color: {COLORS['bg_card']};
            }}
            QCheckBox::indicator:checked {{
                background-color: {COLORS['primary']};
                border-color: {COLORS['primary']};
            }}
        ''')
        layout.addWidget(self.break_check, alignment=Qt.AlignmentFlag.AlignCenter)
        
        layout.addStretch()
        
        self.update_stats()
    
    def update_ui_texts(self):
        """Update all UI texts when language changes"""
        self.title_label.setText(_('pomodoro.title'))
        self.mode_label.setText(_('pomodoro.timer.focus_time') if not self.is_break else _('pomodoro.timer.break_time'))
        self.subject_label.setText(_('pomodoro.subject') + ':')
        self.duration_presets_label.setText(_('pomodoro.duration') + ':')
        self.break_check.setText(_('pomodoro.break.short_break'))
        
        # Update buttons
        self.start_btn.setText(_('pomodoro.controls.start'))
        self.pause_btn.setText(_('pomodoro.controls.pause'))
        self.reset_btn.setText(_('pomodoro.controls.reset'))
        
        for btn, key in self.duration_btns:
            btn.setText(_(key))
            
        # Update stat labels
        for key, (lbl, val) in self.stats_labels.items():
            lbl.setText(_(key))
            
        # Update subjects
        self.subject_combo.clear()
        self.subject_combo.addItems(lang_mgr.translations.get(lang_mgr.current_language, {}).get('pomodoro', {}).get('subjects', []))
        
        self.update_stats()

    def set_subject(self, subject):
        self.current_subject = subject
    
    def set_duration(self, minutes):
        self.sound.play_button()
        self.time_left = minutes * 60
        self.original_time = minutes * 60
        self.update_display()
    
    def start_timer(self):
        self.sound.play_notification()
        self.is_running = True
        self.timer.start(1000)  # Update every second
        self.start_btn.setEnabled(False)
        self.pause_btn.setEnabled(True)
        
        if self.break_check.isChecked() and not self.is_break:
            self.sound.start_progress_loop()
    
    def pause_timer(self):
        self.sound.play_button()
        self.is_running = False
        self.timer.stop()
        self.start_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.sound.stop_progress_loop()
    
    def reset_timer(self):
        self.sound.play_button()
        self.is_running = False
        self.timer.stop()
        self.time_left = self.original_time
        self.is_break = False
        self.mode_label.setText(_('pomodoro.timer.focus_time'))
        self.mode_label.setStyleSheet(f'color: {COLORS["success"]}; font-size: 14px; font-weight: 600; letter-spacing: 2px;')
        self.update_display()
        self.start_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.sound.stop_progress_loop()
    
    def update_timer(self):
        self.time_left -= 1
        
        if self.time_left <= 0:
            self.timer_finished()
        else:
            self.update_display()
    
    def update_display(self):
        minutes = self.time_left // 60
        seconds = self.time_left % 60
        self.timer_label.setText(f'{minutes:02d}:{seconds:02d}')
        
        progress = (self.time_left / self.original_time) * 100
        self.progress_bar.setValue(int(progress))
    
    def timer_finished(self):
        self.timer.stop()
        self.is_running = False
        self.sound.stop_progress_loop()
        
        if self.is_break:
            # Break finished, back to focus
            self.sound.play_celebration()
            self.is_break = False
            self.time_left = self.original_time
            self.mode_label.setText(_('pomodoro.timer.focus_time'))
            self.mode_label.setStyleSheet(f'color: {COLORS["success"]}; font-size: 14px; font-weight: 600; letter-spacing: 2px;')
        else:
            # Focus session finished
            self.sound.play_celebration()
            
            # Save to database
            duration = self.original_time // 60
            self.db.add_pomodoro_session(duration, self.current_subject, True)
            self.update_stats()
            
            if self.break_check.isChecked():
                # Start break
                self.is_break = True
                self.time_left = 5 * 60
                self.original_time = 5 * 60
                self.mode_label.setText(_('pomodoro.timer.break_time'))
                self.mode_label.setStyleSheet(f'color: {COLORS["secondary"]}; font-size: 14px; font-weight: 600; letter-spacing: 2px;')
                self.start_timer()
                return
            else:
                self.time_left = self.original_time
        
        self.start_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.update_display()
    
    def update_stats(self):
        stats = self.db.get_pomodoro_stats(1)  # Today's stats
        self.stats_labels['pomodoro.stats.todays_sessions'][1].setText(str(stats['completed_sessions']))


class NotesWidget(QWidget):
    """Notlar ve Ses Kaydı Widget'ı"""
    note_selected = pyqtSignal(int)
    
    def __init__(self, db, sound_manager, audio_recorder, parent=None):
        super().__init__(parent)
        self.db = db
        self.sound = sound_manager
        self.recorder = audio_recorder
        self.current_note_id = None
        self.is_recording = False
        
        self.setup_ui()
        self.load_notes()
    
    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Left panel - Notes list
        left_panel = CardFrame()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(15)
        left_layout.setContentsMargins(20, 20, 20, 20)
        
        # Search bar
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(_('notes.search_placeholder'))
        self.search_input.setStyleSheet(f'''
            QLineEdit {{
                background-color: {COLORS['bg_dark']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 10px 15px;
                font-size: 13px;
            }}
        ''')
        self.search_input.textChanged.connect(self.filter_notes)
        search_layout.addWidget(self.search_input)
        
        left_layout.addLayout(search_layout)
        
        # New note button
        self.new_btn = ModernButton(_('notes.new_note'), 'primary')
        self.new_btn.clicked.connect(self.create_new_note)
        left_layout.addWidget(self.new_btn)
        
        # Notes list
        self.notes_list = QListWidget()
        self.notes_list.setStyleSheet(f'''
            QListWidget {{
                background-color: {COLORS['bg_dark']};
                border: none;
                border-radius: 8px;
                padding: 5px;
            }}
            QListWidget::item {{
                background-color: {COLORS['bg_card']};
                border-radius: 8px;
                padding: 15px;
                margin: 5px;
                color: {COLORS['text_primary']};
            }}
            QListWidget::item:hover {{
                background-color: {COLORS['bg_hover']};
            }}
            QListWidget::item:selected {{
                background-color: {COLORS['primary']};
                color: white;
            }}
        ''')
        self.notes_list.itemClicked.connect(self.load_note)
        left_layout.addWidget(self.notes_list)
        
        layout.addWidget(left_panel, 1)
        
        # Right panel - Editor
        right_panel = CardFrame()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(15)
        right_layout.setContentsMargins(25, 25, 25, 25)
        
        # Title input
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText(_('notes.form.title'))
        self.title_input.setStyleSheet(f'''
            QLineEdit {{
                background-color: {COLORS['bg_dark']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 10px;
                padding: 15px;
                font-size: 18px;
                font-weight: 600;
            }}
        ''')
        right_layout.addWidget(self.title_input)
        
        # Subject selector
        subject_layout = QHBoxLayout()
        self.subject_label = QLabel(_('notes.form.subject') + ':')
        self.subject_label.setStyleSheet(f'color: {COLORS["text_secondary"]};')
        subject_layout.addWidget(self.subject_label)
        
        self.subject_combo = QComboBox()
        self.subject_combo.setEditable(True)
        self.subject_combo.addItems(lang_mgr.translations.get(lang_mgr.current_language, {}).get('pomodoro', {}).get('subjects', []))
        self.subject_combo.setStyleSheet(f'''
            QComboBox {{
                background-color: {COLORS['bg_dark']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 8px 12px;
            }}
        ''')
        subject_layout.addWidget(self.subject_combo)
        subject_layout.addStretch()
        
        right_layout.addLayout(subject_layout)
        
        # Toolbar
        toolbar_layout = QHBoxLayout()
        
        # Voice record button
        self.record_btn = ModernButton(_('notes.actions.record_voice'), 'secondary')
        self.record_btn.clicked.connect(self.toggle_recording)
        toolbar_layout.addWidget(self.record_btn)
        
        # PDF upload button
        self.pdf_btn = ModernButton(_('notes.actions.attach_pdf'), 'secondary')
        self.pdf_btn.clicked.connect(self.attach_pdf)
        toolbar_layout.addWidget(self.pdf_btn)
        
        # View PDF button
        self.view_pdf_btn = ModernButton(_('notes.actions.view_pdf'), 'secondary')
        self.view_pdf_btn.clicked.connect(self.view_pdf)
        self.view_pdf_btn.setEnabled(False)
        toolbar_layout.addWidget(self.view_pdf_btn)
        
        toolbar_layout.addStretch()
        
        # Delete button
        self.delete_btn = ModernButton(_('notes.delete_note'), 'danger')
        self.delete_btn.clicked.connect(self.delete_note)
        self.delete_btn.setEnabled(False)
        toolbar_layout.addWidget(self.delete_btn)
        
        # Save button
        self.save_btn = ModernButton(_('app.save'), 'primary')
        self.save_btn.clicked.connect(self.save_note)
        toolbar_layout.addWidget(self.save_btn)
        
        right_layout.addLayout(toolbar_layout)
        
        # Recording indicator
        self.recording_label = QLabel(_('notes.actions.recording'))
        self.recording_label.setStyleSheet(f'color: {COLORS["danger"]}; font-weight: 600;')
        self.recording_label.hide()
        right_layout.addWidget(self.recording_label)
        
        # Audio indicator
        self.audio_label = QLabel('')
        self.audio_label.setStyleSheet(f'color: {COLORS["success"]};')
        right_layout.addWidget(self.audio_label)
        
        # PDF indicator
        self.pdf_label = QLabel('')
        self.pdf_label.setStyleSheet(f'color: {COLORS["info"]};')
        right_layout.addWidget(self.pdf_label)
        
        # Content editor
        self.content_edit = QTextEdit()
        self.content_edit.setPlaceholderText(_('notes.form.content_placeholder'))
        self.content_edit.setStyleSheet(f'''
            QTextEdit {{
                background-color: {COLORS['bg_dark']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 10px;
                padding: 15px;
                font-size: 14px;
                line-height: 1.6;
            }}
        ''')
        right_layout.addWidget(self.content_edit)
        
        layout.addWidget(right_panel, 2)
        
        self.current_audio_path = None
        self.current_pdf_path = None
    
    def update_ui_texts(self):
        """Update all UI texts when language changes"""
        self.search_input.setPlaceholderText(_('notes.search_placeholder'))
        self.new_btn.setText(_('notes.new_note'))
        self.title_input.setPlaceholderText(_('notes.form.title'))
        self.subject_label.setText(_('notes.form.subject') + ':')
        self.record_btn.setText(_('notes.actions.record_voice') if not self.is_recording else _('notes.actions.stop_recording'))
        self.pdf_btn.setText(_('notes.actions.attach_pdf'))
        self.view_pdf_btn.setText(_('notes.actions.view_pdf'))
        self.delete_btn.setText(_('notes.delete_note'))
        self.save_btn.setText(_('app.save'))
        self.recording_label.setText(_('notes.actions.recording'))
        self.content_edit.setPlaceholderText(_('notes.form.content_placeholder'))
        
        # Update subjects
        self.subject_combo.clear()
        self.subject_combo.addItems(lang_mgr.translations.get(lang_mgr.current_language, {}).get('pomodoro', {}).get('subjects', []))
        
        self.load_notes()

    def load_notes(self):
        self.notes_list.clear()
        notes = self.db.get_notes()
        
        for note in notes:
            subject_text = note[2] if note[2] else _('pomodoro.subjects.0')
            item = QListWidgetItem(f"{note[1]}\n{subject_text}")
            item.setData(Qt.ItemDataRole.UserRole, note[0])
            self.notes_list.addItem(item)
    
    def filter_notes(self, text):
        for i in range(self.notes_list.count()):
            item = self.notes_list.item(i)
            if text.lower() in item.text().lower():
                item.setHidden(False)
            else:
                item.setHidden(True)
    
    def create_new_note(self):
        self.sound.play_button()
        self.current_note_id = None
        self.title_input.clear()
        self.content_edit.clear()
        self.subject_combo.setCurrentText(_('pomodoro.subjects.0'))
        self.current_audio_path = None
        self.current_pdf_path = None
        self.audio_label.setText('')
        self.pdf_label.setText('')
        self.delete_btn.setEnabled(False)
        self.view_pdf_btn.setEnabled(False)
    
    def load_note(self, item):
        self.sound.play_select()
        note_id = item.data(Qt.ItemDataRole.UserRole)
        self.current_note_id = note_id
        
        notes = self.db.get_notes()
        for note in notes:
            if note[0] == note_id:
                self.title_input.setText(note[1])
                self.content_edit.setText(note[2] if note[2] else '')
                self.subject_combo.setCurrentText(note[3] if note[3] else _('pomodoro.subjects.0'))
                self.current_audio_path = note[4]
                self.current_pdf_path = note[5]
                
                if self.current_audio_path:
                    self.audio_label.setText(f'{_("notes.actions.audio_attached")}: {Path(self.current_audio_path).name}')
                else:
                    self.audio_label.setText('')
                
                if self.current_pdf_path:
                    self.pdf_label.setText(f'{_("notes.actions.pdf_attached")}: {Path(self.current_pdf_path).name}')
                    self.view_pdf_btn.setEnabled(True)
                else:
                    self.pdf_label.setText('')
                    self.view_pdf_btn.setEnabled(False)
                
                self.delete_btn.setEnabled(True)
                break
    
    def toggle_recording(self):
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()
    
    def start_recording(self):
        self.sound.play_notification()
        self.is_recording = True
        self.recorder.start_recording()
        self.record_btn.setText(_('notes.actions.stop_recording'))
        self.record_btn.variant = 'danger'
        self.record_btn.apply_style()
        self.recording_label.show()
    
    def stop_recording(self):
        self.sound.play_button()
        self.is_recording = False
        self.current_audio_path = self.recorder.stop_recording()
        self.record_btn.setText(_('notes.actions.record_voice'))
        self.record_btn.variant = 'secondary'
        self.record_btn.apply_style()
        self.recording_label.hide()
        
        if self.current_audio_path:
            self.audio_label.setText(f'{_("notes.actions.audio_attached")}: {Path(self.current_audio_path).name}')
    
    def attach_pdf(self):
        self.sound.play_button()
        file_path, _ = QFileDialog.getOpenFileName(
            self, _('notes.actions.attach_pdf'), '', 'PDF Files (*.pdf)'
        )
        if file_path:
            self.current_pdf_path = file_path
            self.pdf_label.setText(f'{_("notes.actions.pdf_attached")}: {Path(file_path).name}')
            self.view_pdf_btn.setEnabled(True)
    
    def view_pdf(self):
        if self.current_pdf_path and Path(self.current_pdf_path).exists():
            # Open PDF in default viewer
            QDesktopServices.openUrl(QUrl.fromLocalFile(self.current_pdf_path))
    
    def save_note(self):
        self.sound.play_celebration()
        title = self.title_input.text()
        content = self.content_edit.toPlainText()
        subject = self.subject_combo.currentText()
        
        if not title:
            QMessageBox.warning(self, _('app.warning'), _('notes.form.title_placeholder'))
            return
        
        if self.current_note_id:
            self.db.update_note(
                self.current_note_id,
                title=title,
                content=content,
                subject=subject,
                audio_path=self.current_audio_path,
                pdf_path=self.current_pdf_path
            )
        else:
            self.current_note_id = self.db.add_note(
                title=title,
                content=content,
                subject=subject,
                audio_path=self.current_audio_path,
                pdf_path=self.current_pdf_path
            )
        
        self.load_notes()
        self.delete_btn.setEnabled(True)
        QMessageBox.information(self, _('app.success'), _('notes.save_success'))
    
    def delete_note(self):
        if self.current_note_id:
            self.sound.play_caution()
            reply = QMessageBox.question(
                self, _('confirmations.delete_title'),
                _('notes.confirm_delete'),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.db.delete_note(self.current_note_id)
                self.create_new_note()
                self.load_notes()


class ExamsWidget(QWidget):
    """Sınav Takvimi ve Geri Sayım Widget'ı"""
    def __init__(self, db, sound_manager, parent=None):
        super().__init__(parent)
        self.db = db
        self.sound = sound_manager
        self.alert_timer = QTimer()
        self.alert_timer.timeout.connect(self.check_upcoming_exams)
        self.alert_timer.start(60000)  # Check every minute
        
        self.setup_ui()
        self.load_exams()
    
    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Left panel - Exam list
        left_panel = CardFrame()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(15)
        left_layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        self.title_label = QLabel(_('exams.title'))
        self.title_label.setStyleSheet(f'font-size: 24px; font-weight: 700; color: {COLORS["text_primary"]};')
        left_layout.addWidget(self.title_label)
        
        # Add exam button
        self.add_btn = ModernButton(_('exams.add_exam'), 'primary')
        self.add_btn.clicked.connect(self.add_exam)
        left_layout.addWidget(self.add_btn)
        
        # Exams list
        self.exams_list = QListWidget()
        self.exams_list.setStyleSheet(f'''
            QListWidget {{
                background-color: {COLORS['bg_dark']};
                border: none;
                border-radius: 8px;
                padding: 5px;
            }}
            QListWidget::item {{
                background-color: {COLORS['bg_card']};
                border-radius: 8px;
                padding: 15px;
                margin: 5px;
                color: {COLORS['text_primary']};
            }}
            QListWidget::item:hover {{
                background-color: {COLORS['bg_hover']};
            }}
            QListWidget::item:selected {{
                background-color: {COLORS['primary']};
                color: white;
            }}
        ''')
        self.exams_list.itemClicked.connect(self.show_exam_details)
        left_layout.addWidget(self.exams_list)
        
        layout.addWidget(left_panel, 1)
        
        # Right panel - Countdown and details
        right_panel = CardFrame()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(20)
        right_layout.setContentsMargins(25, 25, 25, 25)
        
        # Countdown section
        self.countdown_title = QLabel(_('exams.next_exam_countdown'))
        self.countdown_title.setStyleSheet(f'font-size: 18px; font-weight: 600; color: {COLORS["text_secondary"]};')
        right_layout.addWidget(self.countdown_title)
        
        self.countdown_label = QLabel(_('exams.no_exams'))
        self.countdown_label.setStyleSheet(f'''
            font-size: 48px;
            font-weight: 700;
            color: {COLORS['primary']};
        ''')
        self.countdown_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.addWidget(self.countdown_label)
        
        # Exam details card
        details_card = CardFrame()
        details_card.setStyleSheet(f'''
            QFrame {{
                background-color: {COLORS['bg_dark']};
                border-radius: 12px;
                border: 1px solid {COLORS['border']};
            }}
        ''')
        details_layout = QFormLayout(details_card)
        details_layout.setSpacing(15)
        details_layout.setContentsMargins(20, 20, 20, 20)
        
        self.detail_labels = {}
        self.detail_fields = [
            ('exams.details.subject', 'Ders'),
            ('exams.details.date', 'Tarih'),
            ('exams.details.time', 'Saat'),
            ('exams.details.location', 'Yer'),
            ('exams.details.duration', 'Süre'),
            ('exams.details.priority', 'Öncelik')
        ]
        
        for key, default_text in self.detail_fields:
            lbl = QLabel('-')
            lbl.setStyleSheet(f'color: {COLORS["text_primary"]}; font-size: 14px;')
            self.detail_labels[key] = lbl
            details_layout.addRow(QLabel(_(key, default_text) + ':'), lbl)
        
        right_layout.addWidget(details_card)
        
        # Delete button
        self.delete_btn = ModernButton(_('exams.delete_exam'), 'danger')
        self.delete_btn.clicked.connect(self.delete_exam)
        self.delete_btn.setEnabled(False)
        right_layout.addWidget(self.delete_btn)
        
        right_layout.addStretch()
        layout.addWidget(right_panel, 1)
        
        # Countdown timer
        self.countdown_timer = QTimer()
        self.countdown_timer.timeout.connect(self.update_countdown)
        self.countdown_timer.start(1000)
        
        self.current_exam = None
    
    def update_ui_texts(self):
        """Update all UI texts when language changes"""
        self.title_label.setText(_('exams.title'))
        self.add_btn.setText(_('exams.add_exam'))
        self.countdown_title.setText(_('exams.next_exam_countdown'))
        self.delete_btn.setText(_('exams.delete_exam'))
        
        if not self.current_exam:
            self.countdown_label.setText(_('exams.no_exams'))
            
        # Re-layout the form to update row labels
        self.load_exams()

    def load_exams(self):
        self.exams_list.clear()
        exams = self.db.get_exams()
        
        for exam in exams:
            # Handle datetime with or without microseconds
            exam_date_str = exam[3]
            try:
                exam_date = datetime.strptime(exam_date_str, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                # Try with microseconds format
                try:
                    exam_date = datetime.strptime(exam_date_str, '%Y-%m-%d %H:%M:%S.%f')
                except ValueError:
                    # Fallback to ISO format
                    exam_date = datetime.fromisoformat(exam_date_str.replace('T', ' '))
            
            now = datetime.now()
            diff = exam_date - now
            days_left = diff.days
            
            if diff.total_seconds() < 0:
                status = _('exams.status.past')
            elif days_left == 0:
                status = _('exams.status.today')
            elif days_left == 1:
                status = _('exams.status.tomorrow')
            else:
                status = f'{days_left} {_("exams.status.days_left")}'
            
            item_text = f"{exam[1]} - {exam[2]}\n{exam_date.strftime('%d %B %Y %H:%M')} - {status}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, exam[0])
            self.exams_list.addItem(item)
        
        self.update_next_exam()
    
    def update_next_exam(self):
        exams = self.db.get_upcoming_exams(365)
        if exams:
            self.current_exam = exams[0]
            self.update_countdown()
            
            # Update details
            exam_date_str = self.current_exam[3]
            try:
                exam_date = datetime.strptime(exam_date_str, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                try:
                    exam_date = datetime.strptime(exam_date_str, '%Y-%m-%d %H:%M:%S.%f')
                except ValueError:
                    exam_date = datetime.fromisoformat(exam_date_str.replace('T', ' '))
            
            self.detail_labels['exams.details.subject'].setText(self.current_exam[2])
            self.detail_labels['exams.details.date'].setText(exam_date.strftime('%d %B %Y'))
            self.detail_labels['exams.details.time'].setText(exam_date.strftime('%H:%M'))
            self.detail_labels['exams.details.location'].setText(self.current_exam[5] or '-')
            self.detail_labels['exams.details.duration'].setText(f"{self.current_exam[4]} {_('exams.form.duration_suffix')}" if self.current_exam[4] else '-')
            
            priorities = lang_mgr.translations.get(lang_mgr.current_language, {}).get('exams', {}).get('priorities', [])
            p_idx = min(self.current_exam[6], len(priorities)-1) if priorities else 0
            priority_text = priorities[p_idx] if priorities else '-'
            self.detail_labels['exams.details.priority'].setText(priority_text)
        else:
            self.current_exam = None
            self.countdown_label.setText(_('exams.no_exams'))
    
    def update_countdown(self):
        if not self.current_exam:
            self.countdown_label.setText(_('exams.no_exams'))
            return
        
        # Handle datetime with or without microseconds
        exam_date_str = self.current_exam[3]
        try:
            exam_date = datetime.strptime(exam_date_str, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            try:
                exam_date = datetime.strptime(exam_date_str, '%Y-%m-%d %H:%M:%S.%f')
            except ValueError:
                exam_date = datetime.fromisoformat(exam_date_str.replace('T', ' '))
        
        now = datetime.now()
        diff = exam_date - now
        
        if diff.total_seconds() > 0:
            days = diff.days
            hours, remainder = divmod(diff.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            
            d_str = f'{days}{_("exams.countdown.days")} ' if days > 0 else ""
            self.countdown_label.setText(f'{d_str}{hours:02d}{_("exams.countdown.hours")} {minutes:02d}{_("exams.countdown.minutes")} {seconds:02d}{_("exams.countdown.seconds")}')
        else:
            self.countdown_label.setText(_('exams.countdown.exam_now'))
    
    def check_upcoming_exams(self):
        """Yaklaşan sınavları kontrol et ve alarm çal"""
        if not self.current_exam:
            return
        
        # Handle datetime with or without microseconds
        exam_date_str = self.current_exam[3]
        try:
            exam_date = datetime.strptime(exam_date_str, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            try:
                exam_date = datetime.strptime(exam_date_str, '%Y-%m-%d %H:%M:%S.%f')
            except ValueError:
                exam_date = datetime.fromisoformat(exam_date_str.replace('T', ' '))
        
        now = datetime.now()
        diff = exam_date - now
        
        # Sınav 5 dakika içindeyse ringtone çal
        if 0 < diff.total_seconds() <= 300:
            self.sound.start_ringtone_loop()
        elif diff.total_seconds() <= 0:
            self.sound.stop_ringtone_loop()
    
    def add_exam(self):
        self.sound.play_button()
        dialog = ExamDialog(self.db, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_exams()
    
    def show_exam_details(self, item):
        self.sound.play_select()
        exam_id = item.data(Qt.ItemDataRole.UserRole)
        exams = self.db.get_exams()
        
        for exam in exams:
            if exam[0] == exam_id:
                # Handle datetime with or without microseconds
                exam_date_str = exam[3]
                try:
                    exam_date = datetime.strptime(exam_date_str, '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    try:
                        exam_date = datetime.strptime(exam_date_str, '%Y-%m-%d %H:%M:%S.%f')
                    except ValueError:
                        exam_date = datetime.fromisoformat(exam_date_str.replace('T', ' '))
                
                self.detail_labels['exams.details.subject'].setText(exam[2])
                self.detail_labels['exams.details.date'].setText(exam_date.strftime('%d %B %Y'))
                self.detail_labels['exams.details.time'].setText(exam_date.strftime('%H:%M'))
                self.detail_labels['exams.details.location'].setText(exam[5] or '-')
                self.detail_labels['exams.details.duration'].setText(f"{exam[4]} {_('exams.form.duration_suffix')}" if exam[4] else '-')
                
                priorities = lang_mgr.translations.get(lang_mgr.current_language, {}).get('exams', {}).get('priorities', [])
                p_idx = min(exam[6], len(priorities)-1) if priorities else 0
                priority_text = priorities[p_idx] if priorities else '-'
                self.detail_labels['exams.details.priority'].setText(priority_text)
                
                self.current_exam = exam
                self.delete_btn.setEnabled(True)
                break
    
    def delete_exam(self):
        if self.current_exam:
            self.sound.play_caution()
            reply = QMessageBox.question(
                self, _('confirmations.delete_title'),
                _('exams.confirm_delete'),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.db.delete_exam(self.current_exam[0])
                self.load_exams()
                self.delete_btn.setEnabled(False)


class ExamDialog(QDialog):
    """Yeni sınav ekleme diyaloğu"""
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle(_('exams.add_exam'))
        self.setMinimumWidth(400)
        self.setStyleSheet(f'''
            QDialog {{
                background-color: {COLORS['bg_dark']};
            }}
            QLabel {{
                color: {COLORS['text_primary']};
            }}
        ''')
        
        layout = QFormLayout(self)
        layout.setSpacing(15)
        
        # Title
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText(_('exams.form.title_placeholder'))
        self.title_input.setStyleSheet(f'''
            QLineEdit {{
                background-color: {COLORS['bg_card']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 10px;
            }}
        ''')
        layout.addRow(_('exams.form.title') + ':', self.title_input)
        
        # Subject
        self.subject_input = QLineEdit()
        self.subject_input.setPlaceholderText(_('exams.form.subject_placeholder'))
        self.subject_input.setStyleSheet(self.title_input.styleSheet())
        layout.addRow(_('exams.form.subject') + ':', self.subject_input)
        
        # Date & Time
        self.datetime_input = QDateTimeEdit()
        self.datetime_input.setDateTime(QDateTime.currentDateTime())
        self.datetime_input.setCalendarPopup(True)
        self.datetime_input.setStyleSheet(f'''
            QDateTimeEdit {{
                background-color: {COLORS['bg_card']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 10px;
            }}
        ''')
        layout.addRow(_('exams.form.date_time') + ':', self.datetime_input)
        
        # Duration
        self.duration_input = QSpinBox()
        self.duration_input.setRange(0, 300)
        self.duration_input.setSuffix(' ' + _('exams.form.duration_suffix'))
        self.duration_input.setStyleSheet(self.title_input.styleSheet())
        layout.addRow(_('exams.form.duration') + ':', self.duration_input)
        
        # Location
        self.location_input = QLineEdit()
        self.location_input.setPlaceholderText(_('exams.form.location_placeholder'))
        self.location_input.setStyleSheet(self.title_input.styleSheet())
        layout.addRow(_('exams.form.location') + ':', self.location_input)
        
        # Priority
        self.priority_input = QComboBox()
        self.priority_input.addItems(lang_mgr.translations.get(lang_mgr.current_language, {}).get('exams', {}).get('priorities', []))
        self.priority_input.setStyleSheet(f'''
            QComboBox {{
                background-color: {COLORS['bg_card']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 8px;
            }}
        ''')
        layout.addRow(_('exams.form.priority') + ':', self.priority_input)
        
        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = ModernButton(_('app.save'), 'primary')
        save_btn.clicked.connect(self.save_exam)
        cancel_btn = ModernButton(_('app.cancel'), 'secondary')
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addStretch()
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        layout.addRow(btn_layout)
    
    def save_exam(self):
        title = self.title_input.text()
        subject = self.subject_input.text()
        
        if not title or not subject:
            QMessageBox.warning(self, _('app.warning'), _('exams.form.title_placeholder'))
            return
        
        exam_datetime = self.datetime_input.dateTime().toPyDateTime()
        # Remove microseconds to ensure consistent format
        exam_datetime = exam_datetime.replace(microsecond=0)
        duration = self.duration_input.value()
        location = self.location_input.text()
        priority = self.priority_input.currentIndex()
        
        self.db.add_exam(title, subject, exam_datetime, duration, location, priority)
        self.accept()


class LessonsWidget(QWidget):
    """Haftalık Ders Programı Widget'ı"""
    def __init__(self, db, sound_manager, parent=None):
        super().__init__(parent)
        self.db = db
        self.sound = sound_manager
        self.setup_ui()
        self.load_lessons()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title and controls
        header_layout = QHBoxLayout()
        
        self.title_label = QLabel(_('lessons.title'))
        self.title_label.setStyleSheet(f'font-size: 24px; font-weight: 700; color: {COLORS["text_primary"]};')
        header_layout.addWidget(self.title_label)
        
        header_layout.addStretch()
        
        self.add_btn = ModernButton(_('lessons.add_lesson'), 'primary')
        self.add_btn.clicked.connect(self.add_lesson)
        header_layout.addWidget(self.add_btn)
        
        layout.addLayout(header_layout)
        
        # Day tabs
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(f'''
            QTabWidget::pane {{
                background-color: {COLORS['bg_card']};
                border-radius: 12px;
                border: 1px solid {COLORS['border']};
            }}
            QTabBar::tab {{
                background-color: {COLORS['bg_dark']};
                color: {COLORS['text_secondary']};
                padding: 12px 24px;
                border-radius: 8px;
                margin: 4px;
            }}
            QTabBar::tab:selected {{
                background-color: {COLORS['primary']};
                color: white;
            }}
            QTabBar::tab:hover:!selected {{
                background-color: {COLORS['bg_hover']};
            }}
        ''')
        
        self.day_widgets = {}
        self.setup_tabs()
        
        layout.addWidget(self.tabs)
        
        # Today's lessons highlight
        today_card = CardFrame()
        today_layout = QHBoxLayout(today_card)
        today_layout.setSpacing(15)
        today_layout.setContentsMargins(20, 15, 20, 15)
        
        self.today_label = QLabel(_('lessons.todays_lessons'))
        self.today_label.setStyleSheet(f'font-weight: 600; color: {COLORS["text_primary"]};')
        today_layout.addWidget(self.today_label)
        
        self.today_lessons_label = QLabel(_('lessons.no_lessons'))
        self.today_lessons_label.setStyleSheet(f'color: {COLORS["text_secondary"]};')
        today_layout.addWidget(self.today_lessons_label)
        today_layout.addStretch()
        
        layout.addWidget(today_card)

    def setup_tabs(self):
        """Setup or refresh day tabs"""
        self.tabs.clear()
        self.day_widgets.clear()
        days = lang_mgr.translations.get(lang_mgr.current_language, {}).get('lessons', {}).get('days', [])
        
        for i, day in enumerate(days):
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setStyleSheet('background: transparent; border: none;')
            
            container = QWidget()
            container_layout = QVBoxLayout(container)
            container_layout.setSpacing(10)
            container_layout.setContentsMargins(15, 15, 15, 15)
            container_layout.addStretch()
            
            scroll.setWidget(container)
            self.tabs.addTab(scroll, day)
            self.day_widgets[i] = container_layout
    
    def update_ui_texts(self):
        """Update all UI texts when language changes"""
        self.title_label.setText(_('lessons.title'))
        self.add_btn.setText(_('lessons.add_lesson'))
        self.today_label.setText(_('lessons.todays_lessons'))
        
        # Refresh tabs
        current_idx = self.tabs.currentIndex()
        self.setup_tabs()
        self.tabs.setCurrentIndex(current_idx)
        
        self.load_lessons()
    
    def load_lessons(self):
        # Clear existing widgets
        for layout in self.day_widgets.values():
            while layout.count() > 1:
                item = layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
        
        lessons = self.db.get_lessons()
        today_lessons = []
        today = datetime.now().weekday()
        
        for lesson in lessons:
            day = lesson[2]  # day_of_week
            self.add_lesson_card(day, lesson)
            
            if day == today:
                today_lessons.append(f"{lesson[1]} ({lesson[3]}-{lesson[4]})")
        
        if today_lessons:
            self.today_lessons_label.setText('  |  '.join(today_lessons))
        else:
            self.today_lessons_label.setText(_('lessons.no_lessons'))
    
    def add_lesson_card(self, day, lesson):
        if day not in self.day_widgets:
            return
            
        layout = self.day_widgets[day]
        
        # Get the container widget from the layout
        container = layout.parentWidget()
        
        # Create card with proper parent
        card = QFrame(container)
        card.setStyleSheet(f'''
            QFrame {{
                background-color: {lesson[7]}20;
                border-left: 4px solid {lesson[7]};
                border-radius: 8px;
                padding: 15px;
            }}
        ''')
        
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(5)
        card_layout.setContentsMargins(15, 15, 15, 15)
        
        # Subject and time
        header = QHBoxLayout()
        subject_lbl = QLabel(lesson[1])  # subject
        subject_lbl.setStyleSheet(f'font-weight: 700; font-size: 16px; color: {lesson[7]};')  # color
        header.addWidget(subject_lbl)
        
        time_lbl = QLabel(f"{lesson[3]} - {lesson[4]}")  # start_time - end_time
        time_lbl.setStyleSheet(f'color: {COLORS["text_secondary"]}; font-size: 13px;')
        header.addWidget(time_lbl)
        header.addStretch()
        
        card_layout.addLayout(header)
        
        # Room and teacher
        if lesson[5] or lesson[6]:  # room or teacher
            info_lbl = QLabel()
            info_parts = []
            if lesson[5]:  # room
                info_parts.append(f"{_('lessons.lesson_card.room')}: {lesson[5]}")
            if lesson[6]:  # teacher
                info_parts.append(f"{_('lessons.lesson_card.teacher')}: {lesson[6]}")
            info_lbl.setText('  |  '.join(info_parts))
            info_lbl.setStyleSheet(f'color: {COLORS["text_muted"]}; font-size: 12px;')
            card_layout.addWidget(info_lbl)
        
        # Delete button
        delete_btn = QPushButton(_('app.delete'))
        delete_btn.setStyleSheet(f'''
            QPushButton {{
                background: transparent;
                color: {COLORS['danger']};
                border: none;
                font-size: 11px;
            }}
        ''')
        delete_btn.clicked.connect(lambda: self.delete_lesson(lesson[0]))  # id
        card_layout.addWidget(delete_btn, alignment=Qt.AlignmentFlag.AlignRight)
        
        # Insert BEFORE the stretch widget (at position count-1)
        insert_pos = layout.count() - 1
        if insert_pos < 0:
            insert_pos = 0
        layout.insertWidget(insert_pos, card)
        
        # Ensure card is shown
        card.show()
    
    def add_lesson(self):
        self.sound.play_button()
        dialog = LessonDialog(self.db, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_lessons()
    
    def delete_lesson(self, lesson_id):
        self.sound.play_caution()
        reply = QMessageBox.question(
            self, _('confirmations.delete_title'),
            _('lessons.confirm_delete'),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.db.delete_lesson(lesson_id)
            self.load_lessons()


class LessonDialog(QDialog):
    """Yeni ders ekleme diyaloğu"""
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle(_('lessons.add_lesson'))
        self.setMinimumWidth(350)
        self.setStyleSheet(f'''
            QDialog {{
                background-color: {COLORS['bg_dark']};
            }}
            QLabel {{
                color: {COLORS['text_primary']};
            }}
        ''')
        
        layout = QFormLayout(self)
        layout.setSpacing(15)
        
        # Subject
        self.subject_input = QLineEdit()
        self.subject_input.setPlaceholderText(_('lessons.form.subject_placeholder'))
        self.subject_input.setStyleSheet(f'''
            QLineEdit {{
                background-color: {COLORS['bg_card']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 10px;
            }}
        ''')
        layout.addRow(_('lessons.form.subject') + ':', self.subject_input)
        
        # Day
        self.day_input = QComboBox()
        self.day_input.addItems(lang_mgr.translations.get(lang_mgr.current_language, {}).get('lessons', {}).get('days', []))
        self.day_input.setStyleSheet(f'''
            QComboBox {{
                background-color: {COLORS['bg_card']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 8px;
            }}
        ''')
        layout.addRow(_('lessons.form.day') + ':', self.day_input)
        
        # Start time
        self.start_time = QTimeEdit()
        self.start_time.setDisplayFormat('HH:mm')
        self.start_time.setStyleSheet(self.subject_input.styleSheet())
        layout.addRow(_('lessons.form.start_time') + ':', self.start_time)
        
        # End time
        self.end_time = QTimeEdit()
        self.end_time.setDisplayFormat('HH:mm')
        self.end_time.setTime(QTime(10, 0))
        self.end_time.setStyleSheet(self.subject_input.styleSheet())
        layout.addRow(_('lessons.form.end_time') + ':', self.end_time)
        
        # Room
        self.room_input = QLineEdit()
        self.room_input.setPlaceholderText(_('lessons.form.room_placeholder'))
        self.room_input.setStyleSheet(self.subject_input.styleSheet())
        layout.addRow(_('lessons.form.room') + ':', self.room_input)
        
        # Teacher
        self.teacher_input = QLineEdit()
        self.teacher_input.setPlaceholderText(_('lessons.form.teacher_placeholder'))
        self.teacher_input.setStyleSheet(self.subject_input.styleSheet())
        layout.addRow(_('lessons.form.teacher') + ':', self.teacher_input)
        
        # Color
        self.color_btn = QPushButton(_('lessons.form.color'))
        self.selected_color = '#3498db'
        self.color_btn.clicked.connect(self.select_color)
        self.color_btn.setStyleSheet(f'''
            QPushButton {{
                background-color: {self.selected_color};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px;
            }}
        ''')
        layout.addRow(_('lessons.form.color') + ':', self.color_btn)
        
        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = ModernButton(_('app.save'), 'primary')
        save_btn.clicked.connect(self.save_lesson)
        cancel_btn = ModernButton(_('app.cancel'), 'secondary')
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addStretch()
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        layout.addRow(btn_layout)
    
    def select_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.selected_color = color.name()
            self.color_btn.setStyleSheet(f'''
                QPushButton {{
                    background-color: {self.selected_color};
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 10px;
                }}
            ''')
    
    def save_lesson(self):
        subject = self.subject_input.text()
        if not subject:
            QMessageBox.warning(self, _('app.warning'), _('lessons.form.subject_placeholder'))
            return
        
        day = self.day_input.currentIndex()
        start_time = self.start_time.time().toString('HH:mm')
        end_time = self.end_time.time().toString('HH:mm')
        room = self.room_input.text()
        teacher = self.teacher_input.text()
        
        self.db.add_lesson(subject, day, start_time, end_time, room, teacher, self.selected_color)
        self.accept()


class DashboardWidget(QWidget):
    """Tüm özelliklerin özeti dashboard"""
    def __init__(self, db, sound_manager, parent=None):
        super().__init__(parent)
        self.db = db
        self.sound = sound_manager
        self.setup_ui()
        self.update_stats()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Welcome title
        self.welcome_lbl = QLabel(_('app.title'))
        self.welcome_lbl.setStyleSheet(f'''
            font-size: 36px;
            font-weight: 800;
            color: {COLORS['primary']};
        ''')
        layout.addWidget(self.welcome_lbl)
        
        self.subtitle_lbl = QLabel(_('dashboard.subtitle'))
        self.subtitle_lbl.setStyleSheet(f'font-size: 16px; color: {COLORS["text_secondary"]};')
        layout.addWidget(self.subtitle_lbl)
        
        # Stats grid
        stats_grid = QGridLayout()
        stats_grid.setSpacing(15)
        
        self.stat_cards = {}
        self.stat_label_widgets = {} # To store the actual QLabel objects for translation
        self.stat_labels = [
            ('dashboard.stats.focus_sessions_7d', 'Odak Seansları (7g)'),
            ('dashboard.stats.total_focus_time', 'Toplam Odak Süresi'),
            ('dashboard.stats.notes_created', 'Oluşturulan Notlar'),
            ('dashboard.stats.upcoming_exams', 'Yaklaşan Sınavlar')
        ]
        
        for i, (key, default_text) in enumerate(self.stat_labels):
            card = CardFrame()
            card_layout = QVBoxLayout(card)
            card_layout.setSpacing(8)
            card_layout.setContentsMargins(20, 20, 20, 20)
            
            lbl = QLabel(_(key, default_text))
            lbl.setStyleSheet(f'color: {COLORS["text_secondary"]}; font-size: 12px;')
            self.stat_label_widgets[key] = lbl
            
            val = QLabel('0')
            val.setStyleSheet(f'color: {COLORS["text_primary"]}; font-size: 32px; font-weight: 700;')
            
            self.stat_cards[key] = val
            card_layout.addWidget(lbl)
            card_layout.addWidget(val)
            
            stats_grid.addWidget(card, i // 2, i % 2)
        
        layout.addLayout(stats_grid)
        
        # Quick actions
        self.actions_title = QLabel(_('dashboard.quick_actions'))
        self.actions_title.setStyleSheet(f'font-size: 20px; font-weight: 600; color: {COLORS["text_primary"]}; margin-top: 20px;')
        layout.addWidget(self.actions_title)
        
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(15)
        
        self.action_buttons = []
        quick_actions = [
            ('dashboard.actions.start_pomodoro', 'primary'),
            ('dashboard.actions.new_note', 'secondary'),
            ('dashboard.actions.view_schedule', 'secondary'),
            ('dashboard.actions.check_exams', 'secondary')
        ]
        
        for text_key, variant in quick_actions:
            btn = ModernButton(_(text_key), variant)
            actions_layout.addWidget(btn)
            self.action_buttons.append((btn, text_key))
        
        # Connect quick action buttons
        self.action_buttons[0][0].clicked.connect(self.start_pomodoro)
        self.action_buttons[1][0].clicked.connect(self.new_note)
        self.action_buttons[2][0].clicked.connect(self.view_schedule)
        self.action_buttons[3][0].clicked.connect(self.check_exams)
        
        actions_layout.addStretch()
        layout.addLayout(actions_layout)
        
        # Recent activity
        self.activity_title = QLabel(_('dashboard.recent_activity'))
        self.activity_title.setStyleSheet(f'font-size: 20px; font-weight: 600; color: {COLORS["text_primary"]}; margin-top: 20px;')
        layout.addWidget(self.activity_title)
        
        self.activity_list = QListWidget()
        self.activity_list.setStyleSheet(f'''
            QListWidget {{
                background-color: {COLORS['bg_card']};
                border: 1px solid {COLORS['border']};
                border-radius: 12px;
                padding: 10px;
            }}
            QListWidget::item {{
                color: {COLORS['text_secondary']};
                padding: 10px;
                border-bottom: 1px solid {COLORS['border']};
            }}
        ''')
        self.activity_list.setMaximumHeight(200)
        layout.addWidget(self.activity_list)
        
        layout.addStretch()
    
    def update_ui_texts(self):
        """Update all UI texts when language changes"""
        self.welcome_lbl.setText(_('app.title'))
        self.subtitle_lbl.setText(_('dashboard.subtitle'))
        self.actions_title.setText(_('dashboard.quick_actions'))
        self.activity_title.setText(_('dashboard.recent_activity'))
        
        # Update stat labels
        for key, default_text in self.stat_labels:
            if key in self.stat_label_widgets:
                self.stat_label_widgets[key].setText(_(key, default_text))
        
        # Update action buttons
        for btn, text_key in self.action_buttons:
            btn.setText(_(text_key))
        
        # Refresh stats
        self.update_stats()
    
    def update_stats(self):
        # Pomodoro stats
        pomo_stats = self.db.get_pomodoro_stats(7)
        self.stat_cards['dashboard.stats.focus_sessions_7d'].setText(str(pomo_stats['completed_sessions']))
        total_hours = pomo_stats['total_focus_minutes'] // 60
        self.stat_cards['dashboard.stats.total_focus_time'].setText(f'{total_hours}{_("time.hours")}')
        
        # Notes count
        notes = self.db.get_notes()
        self.stat_cards['dashboard.stats.notes_created'].setText(str(len(notes)))
        
        # Upcoming exams
        exams = self.db.get_upcoming_exams(30)
        self.stat_cards['dashboard.stats.upcoming_exams'].setText(str(len(exams)))
        
        # Activity feed
        self.activity_list.clear()
        activities = []
        
        # Recent pomodoro sessions
        daily_stats = self.db.get_daily_pomodoro_stats(7)
        for day, sessions, minutes in daily_stats[-3:]:
            if sessions > 0:
                activities.append(f'{day}: {sessions} {_("pomodoro.stats.completed")} ({minutes} {_("time.minutes")})')
        
        # Recent notes
        notes = self.db.get_notes()[:3]
        for note in notes:
            activities.append(f'{_("notes.created")}: {note[1]}')
        
        # Upcoming exams
        exams = self.db.get_upcoming_exams(7)
        for exam in exams[:3]:
            # Handle datetime with or without microseconds
            exam_date_str = exam[3]
            try:
                exam_date = datetime.strptime(exam_date_str, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                try:
                    exam_date = datetime.strptime(exam_date_str, '%Y-%m-%d %H:%M:%S.%f')
                except ValueError:
                    exam_date = datetime.fromisoformat(exam_date_str.replace('T', ' '))
            days_left = (exam_date - datetime.now()).days
            activities.append(f'{_("exams.title")}: {exam[1]} ({days_left} {_("time.days")})')
        
        for activity in activities[:6]:
            self.activity_list.addItem(activity)
    
    def start_pomodoro(self):
        """Navigate to pomodoro page"""
        self.sound.play_button()
        parent = self.parent()
        while parent and not hasattr(parent, 'navigate_to'):
            parent = parent.parent()
        if parent:
            parent.navigate_to('pomodoro')
    
    def new_note(self):
        """Navigate to notes page"""
        self.sound.play_button()
        parent = self.parent()
        while parent and not hasattr(parent, 'navigate_to'):
            parent = parent.parent()
        if parent:
            parent.navigate_to('notes')
    
    def view_schedule(self):
        """Navigate to lessons page"""
        self.sound.play_button()
        parent = self.parent()
        while parent and not hasattr(parent, 'navigate_to'):
            parent = parent.parent()
        if parent:
            parent.navigate_to('lessons')
    
    def check_exams(self):
        """Navigate to exams page"""
        self.sound.play_button()
        parent = self.parent()
        while parent and not hasattr(parent, 'navigate_to'):
            parent = parent.parent()
        if parent:
            parent.navigate_to('exams')

    def update_ui_texts(self):
        """Update all UI texts when language changes"""
        self.welcome_lbl.setText(_('app.title'))
        self.subtitle_lbl.setText(_('dashboard.subtitle'))
        self.actions_title.setText(_('dashboard.quick_actions'))
        self.activity_title.setText(_('dashboard.recent_activity'))
        
        # Update stat labels
        for key, default_text in self.stat_labels:
            if key in self.stat_label_widgets:
                self.stat_label_widgets[key].setText(_(key, default_text))
        
        # Update action buttons
        for btn, text_key in self.action_buttons:
            btn.setText(_(text_key))
        
        # Refresh stats
        self.update_stats()


class MainWindow(QMainWindow):
    """Ana Uygulama Penceresi"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle(_('app.title'))
        self.setMinimumSize(1200, 800)
        
        # Initialize components
        self.db = DatabaseManager()
        self.sound = SoundManager()
        self.recorder = AudioRecorder()
        self.lang_mgr = get_language_manager()
        
        self.setup_ui()
        self.apply_theme()
        
        # Play startup sound
        self.sound.play_transition_up()
        
        # Load saved language preference
        self.load_language_preference()
    
    def load_language_preference(self):
        """Load saved language from database"""
        saved_lang = self.db.get_setting('language', 'tr')
        if saved_lang in self.lang_mgr.get_available_languages():
            self.lang_mgr.set_language(saved_lang)
            self.refresh_ui_texts()
    
    def refresh_ui_texts(self):
        """Refresh all UI texts after language change"""
        # Update window title
        self.setWindowTitle(_('app.title'))
        
        # Update navigation buttons
        nav_items = [
            ('navigation.dashboard', 'dashboard'),
            ('navigation.pomodoro', 'pomodoro'),
            ('navigation.notes', 'notes'),
            ('navigation.lessons', 'lessons'),
            ('navigation.exams', 'exams')
        ]
        for text_key, page in nav_items:
            if page in self.nav_buttons:
                self.nav_buttons[page].setText(_(text_key))
        
        # Update app title in sidebar
        self.app_title.setText(_('app.title'))
        
        # Refresh ALL pages (not just current) so language is consistent when switching tabs
        self.dashboard_page.update_ui_texts()
        self.pomodoro_page.update_ui_texts()
        self.notes_page.update_ui_texts()
        self.lessons_page.update_ui_texts()
        self.exams_page.update_ui_texts()
    
    def setup_ui(self):
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        
        main_layout = QHBoxLayout(central)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Sidebar
        sidebar = QFrame()
        sidebar.setFixedWidth(250)
        sidebar.setStyleSheet(f'''
            QFrame {{
                background-color: {COLORS['bg_card']};
                border-right: 1px solid {COLORS['border']};
            }}
        ''')
        
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setSpacing(10)
        sidebar_layout.setContentsMargins(20, 30, 20, 20)
        
        # App title
        self.app_title = QLabel(_('app.title'))
        self.app_title.setStyleSheet(f'''
            font-size: 24px;
            font-weight: 800;
            color: {COLORS['primary']};
            padding-bottom: 20px;
        ''')
        sidebar_layout.addWidget(self.app_title)
        
        # Navigation buttons
        self.nav_buttons = {}
        nav_items = [
            ('navigation.dashboard', 'dashboard'),
            ('navigation.pomodoro', 'pomodoro'),
            ('navigation.notes', 'notes'),
            ('navigation.lessons', 'lessons'),
            ('navigation.exams', 'exams')
        ]
        
        for text_key, page in nav_items:
            btn = QPushButton(_(text_key))
            btn.setCheckable(True)
            btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn.setStyleSheet(f'''
                QPushButton {{
                    background-color: transparent;
                    color: {COLORS['text_secondary']};
                    border: none;
                    border-radius: 10px;
                    padding: 15px 20px;
                    text-align: left;
                    font-size: 14px;
                    font-weight: 500;
                }}
                QPushButton:hover {{
                    background-color: {COLORS['bg_hover']};
                    color: {COLORS['text_primary']};
                }}
                QPushButton:checked {{
                    background-color: {COLORS['primary']}20;
                    color: {COLORS['primary']};
                    font-weight: 600;
                }}
            ''')
            btn.clicked.connect(lambda checked, p=page: self.navigate_to(p))
            self.nav_buttons[page] = btn
            sidebar_layout.addWidget(btn)
        
        sidebar_layout.addStretch()
        
        # Language selector
        lang_layout = QHBoxLayout()
        lang_lbl = QLabel(_('app.language') + ':')
        lang_lbl.setStyleSheet(f'color: {COLORS["text_secondary"]}; font-size: 12px;')
        
        self.lang_combo = QComboBox()
        self.lang_combo.setStyleSheet(f'''
            QComboBox {{
                background-color: {COLORS['bg_card']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                padding: 5px;
                font-size: 12px;
                min-width: 100px;
            }}
        ''')
        
        # Populate language combo
        available_langs = self.lang_mgr.get_available_languages()
        for code, name in available_langs.items():
            self.lang_combo.addItem(name, code)
        
        # Set current language
        current_lang = self.lang_mgr.current_language
        index = self.lang_combo.findData(current_lang)
        if index >= 0:
            self.lang_combo.setCurrentIndex(index)
        
        self.lang_combo.currentIndexChanged.connect(self.change_language)
        
        lang_layout.addWidget(lang_lbl)
        lang_layout.addWidget(self.lang_combo)
        sidebar_layout.addLayout(lang_layout)
        
        # Volume control
        volume_layout = QHBoxLayout()
        volume_lbl = QLabel(_('app.volume') + ':')
        volume_lbl.setStyleSheet(f'color: {COLORS["text_secondary"]}; font-size: 12px;')
        
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(70)
        self.volume_slider.setStyleSheet(f'''
            QSlider::groove:horizontal {{
                height: 4px;
                background: {COLORS['border']};
                border-radius: 2px;
            }}
            QSlider::handle:horizontal {{
                width: 16px;
                height: 16px;
                margin: -6px 0;
                background: {COLORS['primary']};
                border-radius: 8px;
            }}
            QSlider::sub-page:horizontal {{
                background: {COLORS['primary']};
                border-radius: 2px;
            }}
        ''')
        self.volume_slider.valueChanged.connect(self.change_volume)
        
        volume_layout.addWidget(volume_lbl)
        volume_layout.addWidget(self.volume_slider)
        sidebar_layout.addLayout(volume_layout)
        
        main_layout.addWidget(sidebar)
        
        # Content area
        self.content_stack = QStackedWidget()
        self.content_stack.setStyleSheet(f'background-color: {COLORS["bg_dark"]};')
        
        # Create pages
        self.dashboard_page = DashboardWidget(self.db, self.sound)
        self.pomodoro_page = PomodoroWidget(self.db, self.sound)
        self.notes_page = NotesWidget(self.db, self.sound, self.recorder)
        self.lessons_page = LessonsWidget(self.db, self.sound)
        self.exams_page = ExamsWidget(self.db, self.sound)
        
        self.content_stack.addWidget(self.dashboard_page)
        self.content_stack.addWidget(self.pomodoro_page)
        self.content_stack.addWidget(self.notes_page)
        self.content_stack.addWidget(self.lessons_page)
        self.content_stack.addWidget(self.exams_page)
        
        main_layout.addWidget(self.content_stack, 1)
        
        # Set initial page
        self.navigate_to('dashboard')
    
    def navigate_to(self, page):
        self.sound.play_button()
        
        # Update button states
        for p, btn in self.nav_buttons.items():
            btn.setChecked(p == page)
        
        # Switch page
        page_map = {
            'dashboard': 0,
            'pomodoro': 1,
            'notes': 2,
            'lessons': 3,
            'exams': 4
        }
        
        self.content_stack.setCurrentIndex(page_map[page])
    
    def change_language(self, index):
        """Handle language change from combo box"""
        lang_code = self.lang_combo.itemData(index)
        if lang_code and lang_code != self.lang_mgr.current_language:
            if self.lang_mgr.set_language(lang_code):
                # Save preference
                self.db.set_setting('language', lang_code)
                # Refresh UI
                self.refresh_ui_texts()
                # Play sound
                self.sound.play_notification()
                # Show confirmation
                QMessageBox.information(self, _('app.success'), _('settings.language.language_changed'))
    
    def change_volume(self, value):
        """Handle volume change"""
        self.sound.set_volume(value / 100)
    
    def apply_theme(self):
        self.setStyleSheet(f'''
            QMainWindow {{
                background-color: {COLORS['bg_dark']};
            }}
            QMessageBox {{
                background-color: {COLORS['bg_dark']};
            }}
            QMessageBox QLabel {{
                color: {COLORS['text_primary']};
            }}
            QMessageBox QPushButton {{
                background-color: {COLORS['primary']};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
            }}
        ''')
    
    def closeEvent(self, event):
        self.sound.play_transition_down()
        self.recorder.cleanup()
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Set application font
    font = QFont('Segoe UI', 10)
    app.setFont(font)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
