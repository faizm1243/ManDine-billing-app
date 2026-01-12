import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget,
    QWidget, QLabel, QVBoxLayout
)
from PyQt5.QtCore import Qt

from database import initialize_database
from login import LoginWindow


class MainWindow(QMainWindow):
    def __init__(self, user):
        super().__init__()
        self.user = user

        self.setWindowTitle("ManDine POS")
        self.resize(1100, 650)

        tabs = QTabWidget()
        tabs.setTabPosition(QTabWidget.North)

        tabs.addTab(self.placeholder("Order Details (Coming Next)"), "Order Details")
        tabs.addTab(self.placeholder("Menu (Locked)"), "Menu")
        tabs.addTab(self.placeholder("Status (Analytics)"), "Status")
        tabs.addTab(self.placeholder("History"), "History")

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


main_window = None  # global reference

def launch_main_app(user):
    global main_window
    main_window = MainWindow(user)
    main_window.show()


if __name__ == "__main__":
    # Initialize DB (safe to call multiple times)
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
