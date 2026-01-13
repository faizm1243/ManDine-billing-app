import sqlite3
from config import get_db_path

# -----------------------------
# Order state machine (single source of truth)
# -----------------------------
ORDER_STATES = [
    "NEW",              # Created by receptionist
    "SENT_TO_KITCHEN",  # Sent to kitchen (KOT)
    "COOKING",          # Kitchen accepted
    "READY",            # Food ready
    "SERVED",           # Completed
]

# -----------------------------
# DB helpers
# -----------------------------
def get_db_name():
    return get_db_path()


def get_connection():
    return sqlite3.connect(get_db_name(), timeout=30)


# -----------------------------
# Database initialization
# -----------------------------
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

    # -----------------------------
    # Role → Permission mapping
    # -----------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS role_permissions (
        role TEXT NOT NULL,
        permission TEXT NOT NULL,
        PRIMARY KEY (role, permission)
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
    # Orders (state machine backbone)
    # -----------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id TEXT UNIQUE NOT NULL,
        customer_name TEXT,
        customer_phone TEXT,
        status TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # -----------------------------
    # Orders (for future steps – state machine ready)
    # -----------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_number TEXT UNIQUE,
        customer_name TEXT,
        phone TEXT,
        status TEXT,
        payment_mode TEXT,
        source TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # -----------------------------
    # KOT / Order status history
    # -----------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS order_status_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER,
        status TEXT,
        changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(order_id) REFERENCES orders(id)
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
    # Default role permissions
    # (Admin implicitly has ALL permissions)
    # -----------------------------
    default_permissions = {
        "receptionist": [
            "view_orders",
            "create_order",
            "print_bill",
            "view_history"
        ],
        "kitchen": [
            "view_kitchen",
            "update_kitchen_status"
        ],
        "cashier": [
            "view_orders",
            "print_bill",
            "view_history"
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

def update_order_status(order_id, new_status):
    if new_status not in ORDER_STATES:
        raise ValueError(f"Invalid order state: {new_status}")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE orders SET status=? WHERE order_id=?",
        (new_status, order_id)
    )

    conn.commit()
    conn.close()

