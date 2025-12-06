from PyQt5 import QtWidgets, QtGui, QtCore
from db_con import DBConnection
from qr_generator import generate_user_qr
from vehicle_gui import VehicleForm

db = DBConnection()

class RegisterForm(QtWidgets.QDialog):
    def __init__(self, db_instance=None, user_type="Student", parent=None):
        super().__init__(parent)
        self.db = db_instance or db
        self.user_type = user_type
        self.setWindowTitle(f"Register {self.user_type}")
        self.setFixedSize(480, 520)
        self.init_ui()

    def init_ui(self):
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(20, 14, 20, 14)

        title = QtWidgets.QLabel(f"Register {self.user_type}")
        title.setFont(QtGui.QFont("Arial", 16, QtGui.QFont.Bold))
        title.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(title)

        self.name_var = QtWidgets.QLineEdit(); self.name_var.setPlaceholderText("Full Name")
        self.age_var = QtWidgets.QLineEdit(); self.age_var.setPlaceholderText("Age")
        self.address_var = QtWidgets.QLineEdit(); self.address_var.setPlaceholderText("Address")
        self.contact_var = QtWidgets.QLineEdit(); self.contact_var.setPlaceholderText("Contact Number")
        self.department_var = QtWidgets.QLineEdit(); self.department_var.setPlaceholderText("Department (professors)")
        self.sr_code_var = QtWidgets.QLineEdit(); self.sr_code_var.setPlaceholderText("SR Code (students)")
        self.work_type_var = QtWidgets.QLineEdit(); self.work_type_var.setPlaceholderText("Work Type (workers)")

        for w in (self.name_var, self.age_var, self.address_var, self.contact_var):
            layout.addWidget(w)

        # conditional fields
        if self.user_type == "Student":
            layout.addWidget(self.sr_code_var)
        elif self.user_type == "Professor":
            layout.addWidget(self.department_var)
        elif self.user_type == "Worker":
            layout.addWidget(self.work_type_var)

        self.register_btn = QtWidgets.QPushButton("Register")
        self.register_btn.clicked.connect(self.submit)
        self.register_btn.setStyleSheet("background-color:#1abc9c; color:white; padding:8px; font-weight:bold;")
        layout.addWidget(self.register_btn)

        self.setLayout(layout)

    def submit(self):
        t = self.user_type
        name = self.name_var.text().strip()
        contact = self.contact_var.text().strip()
        age = int(self.age_var.text()) if self.age_var.text().isdigit() else None
        address = self.address_var.text().strip()
        department = self.department_var.text().strip() if t == "Professor" else None
        sr_code = self.sr_code_var.text().strip() if t == "Student" else None
        work_type = self.work_type_var.text().strip() if t == "Worker" else None

        if not name or not contact:
            QtWidgets.QMessageBox.warning(self, "Validation", "Name and Contact are required")
            return

        sql = """
        INSERT INTO register (type, name, age, address, contact_number, department, sr_code, work_type)
        VALUES (?,?,?,?,?,?,?,?)
        """
        reg_id = self.db.insert(sql, (t, name, age, address, contact, department, sr_code, work_type))

        sticker_code, qr_file = generate_user_qr(
            user_id=reg_id, name=name, age=age, address=address, contact=contact,
            department=department, sr_code=sr_code, work_type=work_type
        )

        self.db.update("UPDATE register SET sticker_code=?, qr_file=? WHERE id=?", (sticker_code, qr_file, reg_id))

        QtWidgets.QMessageBox.information(self, "Success", f"User Registered!\nSticker Code: {sticker_code}")

        # open vehicle form for this user
        user_info = {
            'id': reg_id, 'name': name, 'age': age, 'address': address,
            'contact': contact, 'department': department, 'sr_code': sr_code, 'work_type': work_type
        }
        vf = VehicleForm(user_info=user_info, parent=self)
        if vf.exec_() == QtWidgets.QDialog.Accepted:
            self.accept()
        else:
            self.accept()
