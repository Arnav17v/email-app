import sqlite3
import json
from datetime import datetime
from config import DATABASE_PATH, DEFAULT_PROMPTS
import os

class Database:
    def __init__(self):
        self.db_path = DATABASE_PATH
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.init_database()
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Initialize database schema"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Emails table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS emails (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender TEXT NOT NULL,
                subject TEXT NOT NULL,
                body TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                category TEXT DEFAULT NULL,
                action_items TEXT DEFAULT NULL,
                processed INTEGER DEFAULT 0
            )
        """)
        
        # Prompts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS prompts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                prompt_type TEXT NOT NULL,
                template TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        
        # Drafts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS drafts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email_id INTEGER,
                subject TEXT NOT NULL,
                body TEXT NOT NULL,
                metadata TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (email_id) REFERENCES emails (id)
            )
        """)
        
        conn.commit()
        conn.close()
        
        # Load default prompts
        self.load_default_prompts()
    
    def load_default_prompts(self):
        """Load default prompt templates if they don't exist"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        for prompt_type, prompt_data in DEFAULT_PROMPTS.items():
            cursor.execute("SELECT id FROM prompts WHERE prompt_type = ?", (prompt_type,))
            if not cursor.fetchone():
                now = datetime.now().isoformat()
                cursor.execute("""
                    INSERT INTO prompts (name, prompt_type, template, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (prompt_data["name"], prompt_type, prompt_data["template"], now, now))
        
        conn.commit()
        conn.close()
    
    def get_all_emails(self):
        """Get all emails"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, sender, subject, body, timestamp, category, action_items, processed
            FROM emails ORDER BY timestamp DESC
        """)
        emails = cursor.fetchall()
        conn.close()
        return emails
    
    def get_email_by_id(self, email_id):
        """Get email by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, sender, subject, body, timestamp, category, action_items, processed
            FROM emails WHERE id = ?
        """, (email_id,))
        email = cursor.fetchone()
        conn.close()
        return email
    
    def update_email_category(self, email_id, category):
        """Update email category"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE emails SET category = ?, processed = 1
            WHERE id = ?
        """, (category, email_id))
        conn.commit()
        conn.close()
    
    def update_email_actions(self, email_id, action_items):
        """Update email action items"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE emails SET action_items = ?
            WHERE id = ?
        """, (json.dumps(action_items), email_id))
        conn.commit()
        conn.close()
    
    def get_all_prompts(self):
        """Get all prompts"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, name, prompt_type, template, created_at, updated_at
            FROM prompts
        """)
        prompts = cursor.fetchall()
        conn.close()
        return prompts
    
    def get_prompt_by_type(self, prompt_type):
        """Get prompt by type"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, name, prompt_type, template, created_at, updated_at
            FROM prompts WHERE prompt_type = ?
        """, (prompt_type,))
        prompt = cursor.fetchone()
        conn.close()
        return prompt
    
    def update_prompt(self, prompt_type, template):
        """Update prompt template"""
        conn = self.get_connection()
        cursor = conn.cursor()
        now = datetime.now().isoformat()
        cursor.execute("""
            UPDATE prompts SET template = ?, updated_at = ?
            WHERE prompt_type = ?
        """, (template, now, prompt_type))
        conn.commit()
        conn.close()
    
    def create_prompt(self, name, prompt_type, template):
        """Create new prompt"""
        conn = self.get_connection()
        cursor = conn.cursor()
        now = datetime.now().isoformat()
        cursor.execute("""
            INSERT INTO prompts (name, prompt_type, template, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
        """, (name, prompt_type, template, now, now))
        conn.commit()
        conn.close()
    
    def save_draft(self, email_id, subject, body, metadata=None):
        """Save email draft"""
        conn = self.get_connection()
        cursor = conn.cursor()
        now = datetime.now().isoformat()
        cursor.execute("""
            INSERT INTO drafts (email_id, subject, body, metadata, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (email_id, subject, body, json.dumps(metadata) if metadata else None, now))
        draft_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return draft_id
    
    def get_drafts(self):
        """Get all drafts"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT d.id, d.email_id, d.subject, d.body, d.metadata, d.created_at,
                   e.sender, e.subject as original_subject
            FROM drafts d
            LEFT JOIN emails e ON d.email_id = e.id
            ORDER BY d.created_at DESC
        """)
        drafts = cursor.fetchall()
        conn.close()
        return drafts
    
    def delete_draft(self, draft_id):
        """Delete draft"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM drafts WHERE id = ?", (draft_id,))
        conn.commit()
        conn.close()

