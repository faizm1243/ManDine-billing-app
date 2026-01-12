import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget,
    QWidget, QLabel, QVBoxLayout
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
# Permission helper
# -----------------------------
def has_permission(permission):
    if not CURRENT_USER:
        return False

    role = CURRENT_USER[2]  # role column from users table

    # Admin has all permissions
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
            tabs.addTab(self.settings_tab(), "Settings")

        self.setCentralWidget(tabs)

    def placeholder(self, text):
        widget = QWidget()
        layout = QVBoxLayout()

        label = QLabel(text)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-size:16px; color:#555;")

        layout.addWidget(label)
        widget.setLayout(layout)
        return widget

    def settings_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()

        title = QLabel("⚙ Settings (Admin Only)")
        title.setAlignment(Qt.AlignLeft)
        title.setStyleSheet("font-size:18px; font-weight:bold;")

        info = QLabel(
            "• User Management\n"
            "• Role & Permission Control\n"
            "• Theme Selection\n"
            "• Audio Alerts (KOT)\n"
            "• Database / NAS Path\n\n"
            "Settings UI will be enabled step-by-step."
        )
        info.setStyleSheet("font-size:14px;")

        layout.addWidget(title)
        layout.addSpacing(10)
        layout.addWidget(info)
        layout.addStretch()

        widget.setLayout(layout)
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
    # Initialize DB (safe on every run)
    initialize_database()

    app = QApplication(sys.argv)

    # Global UI theme (White / Black / Red)
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
