import sys
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QLineEdit, QMessageBox
)

# Database setup
conn = sqlite3.connect("restaurant.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item TEXT,
    price REAL
)
""")
conn.commit()

class RestaurantApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ManDine Billing App")
        self.setGeometry(100, 100, 500, 400)

        self.item_input = QLineEdit()
        self.item_input.setPlaceholderText("Item name")

        self.price_input = QLineEdit()
        self.price_input.setPlaceholderText("Price")

        add_btn = QPushButton("Add Item")
        add_btn.clicked.connect(self.add_item)

        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["Item", "Price"])

        self.total_label = QLabel("Total: ₹0")

        layout = QVBoxLayout()
        form = QHBoxLayout()
        form.addWidget(self.item_input)
        form.addWidget(self.price_input)
        form.addWidget(add_btn)

        layout.addLayout(form)
        layout.addWidget(self.table)
        layout.addWidget(self.total_label)

        self.setLayout(layout)
        self.load_data()

    def add_item(self):
        item = self.item_input.text()
        price = self.price_input.text()

        if not item or not price:
            QMessageBox.warning(self, "Error", "Enter item and price")
            return

        cursor.execute(
            "INSERT INTO orders (item, price) VALUES (?, ?)",
            (item, float(price))
        )
        conn.commit()
        self.item_input.clear()
        self.price_input.clear()
        self.load_data()

    def load_data(self):
        self.table.setRowCount(0)
        cursor.execute("SELECT item, price FROM orders")
        total = 0

        for row_num, row_data in enumerate(cursor.fetchall()):
            self.table.insertRow(row_num)
            self.table.setItem(row_num, 0, QTableWidgetItem(row_data[0]))
            self.table.setItem(row_num, 1, QTableWidgetItem(str(row_data[1])))
            total += row_data[1]

        self.total_label.setText(f"Total: ₹{total}")

app = QApplication(sys.argv)
window = RestaurantApp()
window.show()
sys.exit(app.exec_())
