"""SQLite persistence for users + test runs."""
import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime

DB_PATH = os.getenv("DB_PATH", "security_tester.db")


@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS test_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                system_prompt TEXT,
                categories TEXT,
                rounds INTEGER,
                pass_rate REAL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)


def create_user(name: str, email: str, password_hash: str) -> bool:
    try:
        with get_conn() as conn:
            conn.execute(
                "INSERT INTO users (name, email, password_hash, created_at) VALUES (?, ?, ?, ?)",
                (name, email.lower().strip(), password_hash, datetime.utcnow().isoformat()),
            )
        return True
    except sqlite3.IntegrityError:
        return False


def get_user_by_email(email: str):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE email = ?", (email.lower().strip(),)
        ).fetchone()
        return dict(row) if row else None


def save_test_run(user_id: int, system_prompt: str, categories: list, rounds: int, pass_rate: float):
    with get_conn() as conn:
        conn.execute(
            """INSERT INTO test_runs (user_id, system_prompt, categories, rounds, pass_rate, created_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (user_id, system_prompt, ",".join(categories), rounds, pass_rate, datetime.utcnow().isoformat()),
        )
