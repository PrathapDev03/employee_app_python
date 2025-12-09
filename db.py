import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), "employees.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    return conn

def init_db():
    """Create tables if they don't exist and seed an admin user."""
    conn = get_connection()
    try:
        cur = conn.cursor()

        # Employee table
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS emp (
                id INTEGER PRIMARY KEY,
                firstName TEXT NOT NULL,
                lastName TEXT NOT NULL,
                salary REAL NOT NULL,
                designation TEXT NOT NULL
            )
            """
        )

        # Users table
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                phone TEXT NOT NULL,
                is_admin INTEGER NOT NULL DEFAULT 0
            )
            """
        )

        # Default admin (demo)
        # Login: email = admin@example.com, phone = 9999999999
        cur.execute(
            """
            INSERT OR IGNORE INTO users (id, name, email, phone, is_admin)
            VALUES (1, 'Admin', 'admin@example.com', '9999999999', 1)
            """
        )

        conn.commit()
    finally:
        conn.close()
