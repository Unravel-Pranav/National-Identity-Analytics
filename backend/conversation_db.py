"""
Production-grade conversation memory management using SQLite.
Handles persistent storage and retrieval of chat conversations.
"""
import sqlite3
import json
import time
from typing import List, Dict, Optional, Any
from pathlib import Path
from contextlib import contextmanager
from datetime import datetime, timedelta


class ConversationDatabase:
    """
    SQLite-based conversation storage with automatic cleanup and context management.
    """
    
    def __init__(self, db_path: str = "conversations.db"):
        """Initialize database connection and create tables."""
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Create tables if they don't exist."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    created_at REAL NOT NULL,
                    last_active REAL NOT NULL,
                    metadata TEXT
                )
            """)
            
            # Messages table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp REAL NOT NULL,
                    metadata TEXT,
                    FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE
                )
            """)
            
            # Create indices for faster queries
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_session_messages 
                ON messages(session_id, timestamp)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_session_active 
                ON sessions(last_active)
            """)
            
            conn.commit()
    
    @contextmanager
    def _get_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        try:
            yield conn
        finally:
            conn.close()
    
    def create_session(self, session_id: str, metadata: Optional[Dict] = None) -> bool:
        """Create a new session."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                now = time.time()
                cursor.execute("""
                    INSERT INTO sessions (session_id, created_at, last_active, metadata)
                    VALUES (?, ?, ?, ?)
                """, (session_id, now, now, json.dumps(metadata or {})))
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            # Session already exists
            return False
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session information."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT session_id, created_at, last_active, metadata
                FROM sessions
                WHERE session_id = ?
            """, (session_id,))
            
            row = cursor.fetchone()
            if row:
                return {
                    'session_id': row['session_id'],
                    'created_at': row['created_at'],
                    'last_active': row['last_active'],
                    'metadata': json.loads(row['metadata']) if row['metadata'] else {}
                }
            return None
    
    def update_session_activity(self, session_id: str):
        """Update the last_active timestamp for a session."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE sessions
                SET last_active = ?
                WHERE session_id = ?
            """, (time.time(), session_id))
            conn.commit()
    
    def add_message(self, session_id: str, role: str, content: str, 
                    metadata: Optional[Dict] = None) -> int:
        """
        Add a message to a session.
        
        Args:
            session_id: Session identifier
            role: Message role (user, assistant, system)
            content: Message content
            metadata: Optional metadata dictionary
        
        Returns:
            Message ID
        """
        # Ensure session exists
        if not self.get_session(session_id):
            self.create_session(session_id)
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO messages (session_id, role, content, timestamp, metadata)
                VALUES (?, ?, ?, ?, ?)
            """, (session_id, role, content, time.time(), json.dumps(metadata or {})))
            conn.commit()
            message_id = cursor.lastrowid
        
        # Update session activity
        self.update_session_activity(session_id)
        
        return message_id
    
    def get_conversation_history(self, session_id: str, limit: Optional[int] = None) -> List[Dict]:
        """
        Get conversation history for a session.
        
        Args:
            session_id: Session identifier
            limit: Maximum number of messages to return (most recent)
        
        Returns:
            List of message dictionaries
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            if limit:
                cursor.execute("""
                    SELECT id, role, content, timestamp, metadata
                    FROM messages
                    WHERE session_id = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """, (session_id, limit))
                rows = cursor.fetchall()
                rows = reversed(rows)  # Return in chronological order
            else:
                cursor.execute("""
                    SELECT id, role, content, timestamp, metadata
                    FROM messages
                    WHERE session_id = ?
                    ORDER BY timestamp ASC
                """, (session_id,))
                rows = cursor.fetchall()
            
            messages = []
            for row in rows:
                messages.append({
                    'id': row['id'],
                    'role': row['role'],
                    'content': row['content'],
                    'timestamp': row['timestamp'],
                    'metadata': json.loads(row['metadata']) if row['metadata'] else {}
                })
            
            return messages
    
    def get_recent_context(self, session_id: str, max_messages: int = 20) -> List[Dict]:
        """
        Get recent conversation context for LLM.
        
        Args:
            session_id: Session identifier
            max_messages: Maximum number of recent messages
        
        Returns:
            List of {role, content} dictionaries suitable for LLM
        """
        messages = self.get_conversation_history(session_id, limit=max_messages)
        return [{'role': msg['role'], 'content': msg['content']} for msg in messages]
    
    def clear_session(self, session_id: str) -> bool:
        """Clear all messages for a session."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
            cursor.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def get_session_count(self, session_id: str) -> int:
        """Get message count for a session."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM messages
                WHERE session_id = ?
            """, (session_id,))
            return cursor.fetchone()['count']
    
    def cleanup_old_sessions(self, days: int = 7):
        """
        Clean up sessions older than specified days.
        
        Args:
            days: Number of days of inactivity before cleanup
        """
        cutoff = time.time() - (days * 24 * 60 * 60)
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM sessions
                WHERE last_active < ?
            """, (cutoff,))
            deleted = cursor.rowcount
            conn.commit()
            return deleted
    
    def get_all_sessions(self, active_only: bool = True, days: int = 7) -> List[Dict]:
        """Get all sessions, optionally filtered by activity."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            if active_only:
                cutoff = time.time() - (days * 24 * 60 * 60)
                cursor.execute("""
                    SELECT s.session_id, s.created_at, s.last_active, 
                           COUNT(m.id) as message_count
                    FROM sessions s
                    LEFT JOIN messages m ON s.session_id = m.session_id
                    WHERE s.last_active >= ?
                    GROUP BY s.session_id
                    ORDER BY s.last_active DESC
                """, (cutoff,))
            else:
                cursor.execute("""
                    SELECT s.session_id, s.created_at, s.last_active,
                           COUNT(m.id) as message_count
                    FROM sessions s
                    LEFT JOIN messages m ON s.session_id = m.session_id
                    GROUP BY s.session_id
                    ORDER BY s.last_active DESC
                """)
            
            sessions = []
            for row in cursor.fetchall():
                sessions.append({
                    'session_id': row['session_id'],
                    'created_at': row['created_at'],
                    'last_active': row['last_active'],
                    'message_count': row['message_count']
                })
            
            return sessions


# Global database instance
_db_instance: Optional[ConversationDatabase] = None


def get_conversation_db() -> ConversationDatabase:
    """Get or create the global conversation database instance."""
    global _db_instance
    if _db_instance is None:
        db_path = Path(__file__).parent / "conversations.db"
        _db_instance = ConversationDatabase(str(db_path))
    return _db_instance

