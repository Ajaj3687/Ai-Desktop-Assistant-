import sqlite3
import os
import datetime

class DatabaseManager:
    def __init__(self, db_path=None):
        if db_path is None:
            # Default database location inside the database folder
            db_dir = os.path.dirname(os.path.abspath(__file__))
            self.db_path = os.path.join(db_dir, "logs.db")
        else:
            self.db_path = db_path
        self.init_db()

    def _get_connection(self):
        """Returns a new database connection."""
        return sqlite3.connect(self.db_path)

    def init_db(self):
        """Initializes the database schema if the file doesn't exist."""
        # Ensure database directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chat_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    sender TEXT NOT NULL,
                    message TEXT NOT NULL
                )
            """)
            conn.commit()

    def log_message(self, sender, message):
        """Saves a conversation turn to the database."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO chat_logs (sender, message) VALUES (?, ?)",
                (sender, message)
            )
            conn.commit()

    def get_recent_logs(self, limit=10):
        """Retrieves the last `limit` chat logs, returned in chronological order."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Fetch last N records ordered by id descending
            cursor.execute(
                "SELECT sender, message, timestamp FROM chat_logs ORDER BY id DESC LIMIT ?",
                (limit,)
            )
            rows = cursor.fetchall()
            # Reverse to get them in chronological order
            return rows[::-1]

    def clear_logs(self):
        """Clears all logged conversations from the database."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM chat_logs")
            conn.commit()
