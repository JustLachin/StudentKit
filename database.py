"""
Database Manager for Student Study Kit
Handles all database operations for notes, exams, lessons, and pomodoro stats
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path


class DatabaseManager:
    def __init__(self, db_path="student_kit.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database with all required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Notes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT,
                subject TEXT,
                audio_path TEXT,
                pdf_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Exams table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS exams (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                subject TEXT NOT NULL,
                exam_date TIMESTAMP NOT NULL,
                duration INTEGER,
                location TEXT,
                priority INTEGER DEFAULT 1,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Lessons table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS lessons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject TEXT NOT NULL,
                day_of_week INTEGER NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                room TEXT,
                teacher TEXT,
                color TEXT DEFAULT '#3498db',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Pomodoro sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pomodoro_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                duration INTEGER NOT NULL,
                subject TEXT,
                completed BOOLEAN DEFAULT 0,
                session_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Settings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    # Notes CRUD
    def add_note(self, title, content, subject=None, audio_path=None, pdf_path=None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO notes (title, content, subject, audio_path, pdf_path)
            VALUES (?, ?, ?, ?, ?)
        ''', (title, content, subject, audio_path, pdf_path))
        conn.commit()
        note_id = cursor.lastrowid
        conn.close()
        return note_id
    
    def get_notes(self, subject=None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        if subject:
            cursor.execute('SELECT * FROM notes WHERE subject = ? ORDER BY updated_at DESC', (subject,))
        else:
            cursor.execute('SELECT * FROM notes ORDER BY updated_at DESC')
        notes = cursor.fetchall()
        conn.close()
        return notes
    
    def update_note(self, note_id, title=None, content=None, subject=None, audio_path=None, pdf_path=None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        updates = []
        params = []
        if title is not None:
            updates.append('title = ?')
            params.append(title)
        if content is not None:
            updates.append('content = ?')
            params.append(content)
        if subject is not None:
            updates.append('subject = ?')
            params.append(subject)
        if audio_path is not None:
            updates.append('audio_path = ?')
            params.append(audio_path)
        if pdf_path is not None:
            updates.append('pdf_path = ?')
            params.append(pdf_path)
        
        updates.append('updated_at = CURRENT_TIMESTAMP')
        params.append(note_id)
        
        query = f"UPDATE notes SET {', '.join(updates)} WHERE id = ?"
        cursor.execute(query, params)
        conn.commit()
        conn.close()
    
    def delete_note(self, note_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM notes WHERE id = ?', (note_id,))
        conn.commit()
        conn.close()
    
    # Exams CRUD
    def add_exam(self, title, subject, exam_date, duration=None, location=None, priority=1, notes=None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO exams (title, subject, exam_date, duration, location, priority, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (title, subject, exam_date, duration, location, priority, notes))
        conn.commit()
        exam_id = cursor.lastrowid
        conn.close()
        return exam_id
    
    def get_exams(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM exams ORDER BY exam_date ASC')
        exams = cursor.fetchall()
        conn.close()
        return exams
    
    def get_upcoming_exams(self, days=7):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM exams 
            WHERE exam_date >= date('now') 
            AND exam_date <= date('now', '+' || ? || ' days')
            ORDER BY exam_date ASC
        ''', (days,))
        exams = cursor.fetchall()
        conn.close()
        return exams
    
    def update_exam(self, exam_id, **kwargs):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        allowed_fields = ['title', 'subject', 'exam_date', 'duration', 'location', 'priority', 'notes']
        updates = []
        params = []
        
        for key, value in kwargs.items():
            if key in allowed_fields:
                updates.append(f'{key} = ?')
                params.append(value)
        
        if updates:
            params.append(exam_id)
            query = f"UPDATE exams SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, params)
            conn.commit()
        conn.close()
    
    def delete_exam(self, exam_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM exams WHERE id = ?', (exam_id,))
        conn.commit()
        conn.close()
    
    # Lessons CRUD
    def add_lesson(self, subject, day_of_week, start_time, end_time, room=None, teacher=None, color='#3498db'):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO lessons (subject, day_of_week, start_time, end_time, room, teacher, color)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (subject, day_of_week, start_time, end_time, room, teacher, color))
        conn.commit()
        lesson_id = cursor.lastrowid
        conn.close()
        return lesson_id
    
    def get_lessons(self, day_of_week=None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        if day_of_week is not None:
            cursor.execute('''
                SELECT * FROM lessons WHERE day_of_week = ? 
                ORDER BY start_time ASC
            ''', (day_of_week,))
        else:
            cursor.execute('SELECT * FROM lessons ORDER BY day_of_week, start_time ASC')
        lessons = cursor.fetchall()
        conn.close()
        return lessons
    
    def get_todays_lessons(self):
        """Get lessons for today (Monday=0, Sunday=6)"""
        today = datetime.now().weekday()
        return self.get_lessons(today)
    
    def update_lesson(self, lesson_id, **kwargs):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        allowed_fields = ['subject', 'day_of_week', 'start_time', 'end_time', 'room', 'teacher', 'color']
        updates = []
        params = []
        
        for key, value in kwargs.items():
            if key in allowed_fields:
                updates.append(f'{key} = ?')
                params.append(value)
        
        if updates:
            params.append(lesson_id)
            query = f"UPDATE lessons SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, params)
            conn.commit()
        conn.close()
    
    def delete_lesson(self, lesson_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM lessons WHERE id = ?', (lesson_id,))
        conn.commit()
        conn.close()
    
    # Pomodoro CRUD
    def add_pomodoro_session(self, duration, subject=None, completed=False):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO pomodoro_sessions (duration, subject, completed)
            VALUES (?, ?, ?)
        ''', (duration, subject, completed))
        conn.commit()
        session_id = cursor.lastrowid
        conn.close()
        return session_id
    
    def get_pomodoro_stats(self, days=7):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT 
                COUNT(*) as total_sessions,
                SUM(CASE WHEN completed = 1 THEN 1 ELSE 0 END) as completed_sessions,
                SUM(CASE WHEN completed = 1 THEN duration ELSE 0 END) as total_focus_minutes
            FROM pomodoro_sessions 
            WHERE session_date >= date('now', '-' || ? || ' days')
        ''', (days,))
        stats = cursor.fetchone()
        conn.close()
        return {
            'total_sessions': stats[0] or 0,
            'completed_sessions': stats[1] or 0,
            'total_focus_minutes': stats[2] or 0
        }
    
    def get_daily_pomodoro_stats(self, days=7):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT 
                date(session_date) as day,
                COUNT(*) as sessions,
                SUM(CASE WHEN completed = 1 THEN duration ELSE 0 END) as minutes
            FROM pomodoro_sessions 
            WHERE session_date >= date('now', '-' || ? || ' days')
            GROUP BY date(session_date)
            ORDER BY day ASC
        ''', (days,))
        stats = cursor.fetchall()
        conn.close()
        return stats
    
    # Settings
    def get_setting(self, key, default=None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else default
    
    def set_setting(self, key, value):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)
        ''', (key, value))
        conn.commit()
        conn.close()
