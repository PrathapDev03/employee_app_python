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
def get_all_employees():
    conn = get_connection()
    employees = []
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, firstName, lastName, salary, designation FROM emp")
        rows = cur.fetchall()
        for row in rows:
            employees.append(
                {
                    "id": row[0],
                    "first_name": row[1],
                    "last_name": row[2],
                    "salary": row[3],
                    "designation": row[4],
                }
            )
    finally:
        conn.close()
    return employees