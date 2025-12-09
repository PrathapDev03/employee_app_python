import os
import sqlite3

# DB file will be created in the project folder
DB_PATH = os.path.join(os.path.dirname(__file__), "employees.db")

def get_connection():
    # row_factory gives dict-like access if needed later
    conn = sqlite3.connect(DB_PATH)
    return conn

def init_db():
    """Create the emp table if it doesn't exist."""
    conn = get_connection()
    try:
        cur = conn.cursor()
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
        conn.commit()
    finally:
        conn.close()
