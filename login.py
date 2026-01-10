from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QMessageBox
)
from database import get_connection

class LoginWindow(QWidget):
    def __init__(self, on_success):
        super().__init__()
        self.on_success = on_success
        self.setWindowTitle("ManDine Login")
        self.setFixedSize(300, 200)

        self.username = QLineEdit()
        self.username.setPlaceholderText("Username")

        self.password = QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(QLineEdit.Password)

        login_btn = QPushButton("Login")
        login_btn.clicked.connect(self.login)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("ManDine POS"))
        layout.addWidget(self.username)
        layout.addWidget(self.password)
        layout.addWidget(login_btn)

        self.setLayout(layout)

    def login(self):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (self.username.text(), self.password.text())
        )

        user = cursor.fetchone()
        conn.close()

        if user:
            self.on_success(user)
            self.close()
        else:
            QMessageBox.warning(self, "Error", "Invalid credentials")

