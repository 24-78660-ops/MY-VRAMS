from PyQt5 import QtWidgets
from db_con import DBConnection
from qr_generator import generate_user_qr

db = DBConnection()

class VehicleForm(QtWidgets.QDialog):
    def __init__(self, user_info, parent=None):
        super().__init__(parent)
        self.user_info = user_info
        self.setWindowTitle("Vehicle Registration")
        self.setGeometry(500, 200, 420, 320)
        self.init_ui()

    def init_ui(self):
        layout = QtWidgets.QVBoxLayout(self)

        self.vtype_entry = QtWidgets.QLineEdit()
        self.vtype_entry.setPlaceholderText("Vehicle Type (e.g., Car)")
        layout.addWidget(self.vtype_entry)

        self.plate_entry = QtWidgets.QLineEdit()
        self.plate_entry.setPlaceholderText("Plate Number")
        layout.addWidget(self.plate_entry)

        self.license_entry = QtWidgets.QLineEdit()
        self.license_entry.setPlaceholderText("License No (optional)")
        layout.addWidget(self.license_entry)

        self.color_entry = QtWidgets.QLineEdit()
        self.color_entry.setPlaceholderText("Color (optional)")
        layout.addWidget(self.color_entry)

        register_btn = QtWidgets.QPushButton("Register Vehicle")
        register_btn.clicked.connect(self.register_vehicle)
        register_btn.setStyleSheet("background-color: #1abc9c; color: white; padding: 8px;")
        layout.addWidget(register_btn)

    def register_vehicle(self):
        # get inputs from the form (simple comment)
        vtype = self.vtype_entry.text().strip()
        plate = self.plate_entry.text().strip()
        license_no = self.license_entry.text().strip()
        color = self.color_entry.text().strip()

        if not vtype or not plate:
            QtWidgets.QMessageBox.warning(self, "Error", "Vehicle Type and Plate Number required!")
            return

        sql = "INSERT INTO vehicle (user_id, vtype, plate, license_no, vcolor, status) VALUES (?,?,?,?,?,?)"
        try:
            vehicle_id = db.insert(sql, (self.user_info['id'], vtype, plate, license_no, color, "Active"))
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "DB Error", f"Failed to insert vehicle:\n{e}")
            return

        try:
            sticker_code, qr_file = generate_user_qr(
                user_id=self.user_info['id'],
                name=self.user_info.get('name'),
                age=self.user_info.get('age'),
                address=self.user_info.get('address'),
                contact=self.user_info.get('contact_number'),
                department=self.user_info.get('department'),
                sr_code=self.user_info.get('sr_code'),
                work_type=self.user_info.get('work_type'),
                vehicle_plate=plate
            )
            db.update("UPDATE vehicle SET sticker_no=?, sticker_file=? WHERE id=?", (sticker_code, qr_file, vehicle_id))
        except Exception as e:
            # non-fatal — vehicle inserted but QR generation failed
            QtWidgets.QMessageBox.warning(self, "QR Error", f"Vehicle added but failed to generate QR:\n{e}")
            self.accept()
            return

        QtWidgets.QMessageBox.information(self, "Success", f"Vehicle Registered!\nSticker: {sticker_code}")
        self.accept()
