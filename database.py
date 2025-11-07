# database.py
import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional

class Database:
    def __init__(self, db_path='bot_database.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """إنشاء جداول قاعدة البيانات"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # جدول المستخدمين
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                is_admin BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # جدول المنشورات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS posts (
                post_id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                media_type TEXT,
                media_file_id TEXT,
                buttons TEXT,
                created_by INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (created_by) REFERENCES users(user_id)
            )
        ''')
        
        # جدول القنوات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS channels (
                channel_id INTEGER PRIMARY KEY,
                channel_username TEXT,
                channel_title TEXT,
                is_active BOOLEAN DEFAULT 1,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # جدول الجدولة
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS schedules (
                schedule_id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER,
                channel_id INTEGER,
                schedule_type TEXT,
                interval_minutes INTEGER,
                fixed_times TEXT,
                is_active BOOLEAN DEFAULT 1,
                last_run TIMESTAMP,
                next_run TIMESTAMP,
                FOREIGN KEY (post_id) REFERENCES posts(post_id),
                FOREIGN KEY (channel_id) REFERENCES channels(channel_id)
            )
        ''')
        
        # جدول السجلات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                action_type TEXT,
                post_id INTEGER,
                channel_id INTEGER,
                status TEXT,
                message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_user(self, user_id: int, username: str = None, first_name: str = None):
        """إضافة مستخدم جديد"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR IGNORE INTO users (user_id, username, first_name)
            VALUES (?, ?, ?)
        ''', (user_id, username, first_name))
        
        conn.commit()
        conn.close()
    
    def add_post(self, content: str, created_by: int, 
                 media_type: str = None, media_file_id: str = None,
                 buttons: str = None) -> int:
        """إضافة منشور جديد"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO posts (content, media_type, media_file_id, buttons, created_by)
            VALUES (?, ?, ?, ?, ?)
        ''', (content, media_type, media_file_id, buttons, created_by))
        
        post_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return post_id
    
    def get_all_posts(self) -> List[Dict]:
        """الحصول على جميع المنشورات"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM posts ORDER BY created_at DESC')
        rows = cursor.fetchall()
        
        posts = [dict(row) for row in rows]
        conn.close()
        
        return posts
    
    def add_channel(self, channel_id: int, channel_username: str = None, 
                    channel_title: str = None):
        """إضافة قناة جديدة"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO channels (channel_id, channel_username, channel_title)
            VALUES (?, ?, ?)
        ''', (channel_id, channel_username, channel_title))
        
        conn.commit()
        conn.close()
    
    def get_active_channels(self) -> List[Dict]:
        """الحصول على القنوات النشطة"""
        conn = sqlite3.connect(self.db_path)
