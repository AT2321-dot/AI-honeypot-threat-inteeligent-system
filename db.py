import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "honeypot.db")


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ip TEXT,
        command TEXT,
        attack_type TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()


def insert_log(ip, command, prediction):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO logs (ip, command, attack_type) VALUES (?, ?, ?)",
        (ip, command, prediction)
    )

    conn.commit()
    conn.close()


def fetch_logs():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT id, ip, command, attack_type FROM logs ORDER BY id DESC")
    data = cursor.fetchall()

    conn.close()
    return data
