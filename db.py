import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), "employees.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    return conn

def init_db():
    """Create tables if they don't exist."""
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

        # Visitors table
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS visitors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        conn.commit()
    finally:
        conn.close()
