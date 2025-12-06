import sys
import hashlib
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox
)
from db_con import DBConnection

db = DBConnection()

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

class CreateAdminWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Create Admin Account")
        self.setFixedSize(420, 350)
        self.setStyleSheet("background-color: #2c3e50; color: white; font-family: Arial;")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(15)

        # Title 
        title = QLabel("Create Admin Account")
        title.setStyleSheet("font-size: 18pt; font-weight: bold;")
        layout.addWidget(title)

        # Username
        user_layout = QHBoxLayout()
        lbl_username = QLabel("Username:")
        lbl_username.setFixedWidth(120)
        self.username_entry = QLineEdit()
        user_layout.addWidget(lbl_username)
        user_layout.addWidget(self.username_entry)
        layout.addLayout(user_layout)

        # Password
        pass_layout = QHBoxLayout()
        lbl_password = QLabel("Password:")
        lbl_password.setFixedWidth(120)
        self.password_entry = QLineEdit()
        self.password_entry.setEchoMode(QLineEdit.Password)
        pass_layout.addWidget(lbl_password)
        pass_layout.addWidget(self.password_entry)
        layout.addLayout(pass_layout)

        # Confirm Password
        confirm_layout = QHBoxLayout()
        lbl_confirm = QLabel("Confirm Password:")
        lbl_confirm.setFixedWidth(120)
        self.confirm_entry = QLineEdit()
        self.confirm_entry.setEchoMode(QLineEdit.Password)
        confirm_layout.addWidget(lbl_confirm)
        confirm_layout.addWidget(self.confirm_entry)
        layout.addLayout(confirm_layout)

        # Buttons
        btn_layout = QHBoxLayout()
        self.create_btn = QPushButton("Create Admin")
        self.create_btn.setStyleSheet(
            "background-color: #1abc9c; color: white; font-weight: bold; padding: 5px;"
        )
        self.create_btn.clicked.connect(self.save_admin)
        self.close_btn = QPushButton("Close")
        self.close_btn.setStyleSheet(
            "background-color: #e74c3c; color: white; font-weight: bold; padding: 5px;"
        )
        self.close_btn.clicked.connect(self.close)
        btn_layout.addWidget(self.create_btn)
        btn_layout.addWidget(self.close_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def save_admin(self):
        username = self.username_entry.text().strip()
        password = self.password_entry.text().strip()
        confirm = self.confirm_entry.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Missing Fields", "All fields must be filled out.")
            return

        if password != confirm:
            QMessageBox.critical(self, "Error", "Passwords do not match.")
            return

        hashed = hash_password(password)

        try:
            # Check if admin exists
            exists = db.fetch_one("SELECT id FROM admins WHERE username = ?", (username,))
            if exists:
                QMessageBox.critical(self, "Error", "Username already exists.")
                return

            # Insert admin
            db.execute("INSERT INTO admins (username, password) VALUES (?, ?)", (username, hashed))
            QMessageBox.information(self, "Success", "Admin account created successfully!")
            
            # Clear fields
            self.username_entry.clear()
            self.password_entry.clear()
            self.confirm_entry.clear()
            
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"An error occurred: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CreateAdminWindow()
    window.show()
    sys.exit(app.exec_())
