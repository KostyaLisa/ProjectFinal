import sqlite3
import bcrypt

class DatabaseManager:
    def __init__(self, db_name="user_auth.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            attempts INTEGER DEFAULT 0,
            blocked INTEGER DEFAULT 0
        )
        """)
        self.conn.commit()

    def add_user(self, username, password):
        if self.get_user(username):  # Проверяем, есть ли пользователь
            return False
        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        self.cursor.execute("INSERT INTO users (username, password, attempts, blocked) VALUES (?, ?, 0, 0)",
                            (username, hashed_password))
        self.conn.commit()
        return True

    def get_user(self, username):
        self.cursor.execute("SELECT password, attempts, blocked FROM users WHERE username=?", (username,))
        return self.cursor.fetchone()

    def update_attempts(self, username, attempts):
        self.cursor.execute("UPDATE users SET attempts=? WHERE username=?", (attempts, username))
        self.conn.commit()

    def block_user(self, username):
        self.cursor.execute("UPDATE users SET blocked=1 WHERE username=?", (username,))
        self.conn.commit()

    def reset_attempts(self, username):
        self.cursor.execute("UPDATE users SET attempts=0 WHERE username=?", (username,))
        self.conn.commit()

    def close(self):
        self.conn.close()
