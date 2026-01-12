import sqlite3
from config import get_db_path

def get_db_name():
    return get_db_path()

def get_connection():
    return sqlite3.connect(get_db_name(), timeout=30)

def initialize_database():
    conn = get_connection()
    cursor = conn.cursor()

    # Branches (multi-branch support)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS branches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        address TEXT,
        phone TEXT
    )
    """)

    # Users (offline login)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL,
        branch_id INTEGER,
        FOREIGN KEY(branch_id) REFERENCES branches(id)
    )
    """)

    # Settings (taxes, printer width, branding)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
    )
    """)

    # Create default admin user (first run only)
    cursor.execute("""
    INSERT OR IGNORE INTO users (username, password, role)
    VALUES ('admin', 'admin123', 'admin')
    """)

    conn.commit()
    conn.close()
