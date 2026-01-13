import sqlite3
from config import get_db_path


def get_db_name():
    return get_db_path()


def get_connection():
    return sqlite3.connect(get_db_name(), timeout=30)


def initialize_database():
    conn = get_connection()
    cursor = conn.cursor()

    # -----------------------------
    # Branches (multi-branch support)
    # -----------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS branches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        address TEXT,
        phone TEXT
    )
    """)

    # -----------------------------
    # Users (offline login)
    # -----------------------------
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

    # Role → Permission mapping
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS role_permissions (
        role TEXT NOT NULL,
        permission TEXT NOT NULL,
        PRIMARY KEY (role, permission)
    )
    """)

    # -----------------------------
    # Role-based permissions
    # -----------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS role_permissions (
        role TEXT NOT NULL,
        permission TEXT NOT NULL,
        UNIQUE(role, permission)
    )
    """)

    # -----------------------------
    # App settings (tax, printer, theme, NAS path, audio, etc.)
    # -----------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
    )
    """)

    # -----------------------------
    # Default admin user (first run only)
    # -----------------------------
    cursor.execute("""
    INSERT OR IGNORE INTO users (username, password, role)
    VALUES ('admin', 'admin123', 'admin')
    """)

    # -----------------------------
    # Default permissions (non-admin)
    # Admin implicitly has ALL permissions
    # -----------------------------
    default_permissions = {
        "reception": [
            "view_orders",
            "create_order",
            "print_bill",
            "view_history"
        ],
        "kitchen": [
            "view_kitchen",
            "update_kitchen_status"
        ]
    }

    for role, permissions in default_permissions.items():
        for permission in permissions:
            cursor.execute(
                "INSERT OR IGNORE INTO role_permissions (role, permission) VALUES (?, ?)",
                (role, permission)
            )

    conn.commit()
    conn.close()
