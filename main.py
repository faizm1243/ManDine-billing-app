import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QLabel, QVBoxLayout
)
from database import initialize_database
from login import LoginWindow

class MainWindow(QMainWindow):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.setWindowTitle("ManDine POS")
        self.resize(1000, 600)

        tabs = QTabWidget()

        tabs.addTab(self.placeholder("Order Details"), "Order Details")
        tabs.addTab(self.placeholder("Menu (Locked)"), "Menu")
        tabs.addTab(self.placeholder("Status"), "Status")
        tabs.addTab(self.placeholder("History"), "History")

        self.setCentralWidget(tabs)

    def placeholder(self, text):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(QLabel(text))
        widget.setLayout(layout)
        return widget

def start_app(user):
    window = MainWindow(user)
    window.show()

if __name__ == "__main__":
    initialize_database()

    app = QApplication(sys.argv)
    login = LoginWindow(start_app)
    login.show()
    sys.exit(app.exec_())
