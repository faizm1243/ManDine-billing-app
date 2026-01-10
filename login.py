from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QMessageBox
)
from PyQt5.QtCore import Qt
from database import get_connection

class LoginWindow(QWidget):
    def __init__(self, on_login_success):
        super().__init__()
        self.on_login_success = on_login_success

        self.setWindowTitle("ManDine POS - Login")
        self.setFixedSize(320, 220)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowMaximizeButtonHint)

        title = QLabel("ManDine POS")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size:18px; font-weight:bold;")

        self.username = QLineEdit()
        self.username.setPlaceholderText("Username")

        self.password = QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(QLineEdit.Password)

        login_btn = QPushButton("Login")
        login_btn.clicked.connect(self.authenticate)

        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.addWidget(title)
        layout.addWidget(self.username)
        layout.addWidget(self.password)
        layout.addWidget(login_btn)

        self.setLayout(layout)

    def authenticate(self):
        username = self.username.text().strip()
        password = self.password.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Error", "Please enter username and password")
            return

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, username, role, branch_id FROM users WHERE username=? AND password=?",
            (username, password)
        )
        user = cursor.fetchone()
        conn.close()

        if user:
            self.on_login_success(user)
            self.close()
        else:
            QMessageBox.critical(self, "Login Failed", "Invalid credentials")
