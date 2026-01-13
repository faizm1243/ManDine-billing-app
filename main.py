import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget,
    QWidget, QLabel, QVBoxLayout,
    QComboBox, QCheckBox, QPushButton, QMessageBox
)
from PyQt5.QtCore import Qt

from database import initialize_database, get_connection
from login import LoginWindow


# -----------------------------
# Global user context
# -----------------------------
CURRENT_USER = None
main_window = None


# -----------------------------
# Permissions master list
# -----------------------------
ALL_PERMISSIONS = [
    ("view_orders", "View Order Details"),
    ("view_menu", "View Menu"),
    ("view_status", "View Status / Analytics"),
    ("view_history", "View Order History"),
    ("view_kitchen", "View Kitchen (KOT)")
]

EDITABLE_ROLES = ["reception", "kitchen"]


# -----------------------------
# Permission helper
# -----------------------------
def has_permission(permission):
    if not CURRENT_USER:
        return False

    role = CURRENT_USER[2]

    # Admin has ALL permissions
    if role == "admin":
        return True

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT 1 FROM role_permissions WHERE role=? AND permission=?",
        (role, permission)
    )
    result = cursor.fetchone()
    conn.close()

    return result is not None


# -----------------------------
# Main Application Window
# -----------------------------
class MainWindow(QMainWindow):
    def __init__(self, user):
        super().__init__()
        self.user = user

        self.setWindowTitle("ManDine POS")
        self.resize(1100, 650)

        tabs = QTabWidget()
        tabs.setTabPosition(QTabWidget.North)

        if has_permission("view_orders"):
            tabs.addTab(self.placeholder("Order Details (Coming Next)"), "Order Detail")

        if has_permission("view_menu"):
            tabs.addTab(self.placeholder("Menu (Locked)"), "Menu")

        if has_permission("view_status"):
            tabs.addTab(self.placeholder("Status (Analytics)"), "Status")

        if has_permission("view_history"):
            tabs.addTab(self.placeholder("History"), "History")

        if has_permission("view_kitchen"):
            tabs.addTab(self.placeholder("Kitchen (KOT)"), "Kitchen")

        # Admin-only Settings tab
        if self.user[2] == "admin":
            tabs.addTab(self.role_permission_editor(), "Settings")

        self.setCentralWidget(tabs)

    # -----------------------------
    # Placeholder tabs
    # -----------------------------
    def placeholder(self, text):
        widget = QWidget()
        layout = QVBoxLayout()
        label = QLabel(text)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-size:16px; color:#555;")
        layout.addWidget(label)
        widget.setLayout(layout)
        return widget

    # -----------------------------
    # Role → Permission Editor (Admin)
    # -----------------------------
    def role_permission_editor(self):
        widget = QWidget()
        layout = QVBoxLayout()

        title = QLabel("⚙ Settings (Admin Only)")
        title.setStyleSheet("font-size:18px; font-weight:bold;")
        layout.addWidget(title)

        subtitle = QLabel("🔐 Role → Permission Editor")
        subtitle.setStyleSheet("font-size:14px; font-weight:bold;")
        layout.addWidget(subtitle)

        layout.addSpacing(10)

        role_select = QComboBox()
        role_select.addItems(EDITABLE_ROLES)

        layout.addWidget(QLabel("Select Role:"))
        layout.addWidget(role_select)

        checkboxes = {}

        for perm_key, perm_label in ALL_PERMISSIONS:
            cb = QCheckBox(perm_label)
            checkboxes[perm_key] = cb
            layout.addWidget(cb)

        def load_permissions():
            role = role_select.currentText()

            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT permission FROM role_permissions WHERE role=?",
                (role,)
            )
            rows = cursor.fetchall()
            conn.close()

            active = {r[0] for r in rows}

            for key, cb in checkboxes.items():
                cb.setChecked(key in active)

        def save_permissions():
            role = role_select.currentText()

            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute(
                "DELETE FROM role_permissions WHERE role=?",
                (role,)
            )

            for key, cb in checkboxes.items():
                if cb.isChecked():
                    cursor.execute(
                        "INSERT INTO role_permissions (role, permission) VALUES (?, ?)",
                        (role, key)
                    )

            conn.commit()
            conn.close()

            QMessageBox.information(
                widget,
                "Saved",
                f"Permissions updated for role: {role}"
            )

        role_select.currentIndexChanged.connect(load_permissions)

        save_btn = QPushButton("Save Permissions")
        save_btn.clicked.connect(save_permissions)

        layout.addSpacing(10)
        layout.addWidget(save_btn)
        layout.addStretch()

        widget.setLayout(layout)

        load_permissions()
        return widget


# -----------------------------
# App launcher after login
# -----------------------------
def launch_main_app(user):
    global CURRENT_USER
    global main_window

    CURRENT_USER = user
    main_window = MainWindow(user)
    main_window.show()


# -----------------------------
# Application Entry Point
# -----------------------------
if __name__ == "__main__":
    initialize_database()

    app = QApplication(sys.argv)

    app.setStyleSheet("""
        QMainWindow {
            background-color: white;
        }
        QLabel {
            color: black;
        }
        QPushButton {
            background-color: #b00020;
            color: white;
            padding: 6px 12px;
            border-radius: 4px;
        }
        QPushButton:hover {
            background-color: #d32f2f;
        }
        QLineEdit {
            padding: 6px;
            border: 1px solid #ccc;
            border-radius: 4px;
        }
        QTabBar::tab {
            padding: 10px 18px;
            font-weight: bold;
        }
        QTabBar::tab:selected {
            background: #b00020;
            color: white;
        }
    """)

    login = LoginWindow(launch_main_app)
    login.show()

    try:
        sys.exit(app.exec_())
    except Exception as e:
        print("FATAL ERROR:", e)
        input("Press ENTER to close...")
