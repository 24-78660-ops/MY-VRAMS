from PyQt5 import QtWidgets, QtCore, QtGui
from db_con import DBConnection
import os

db = DBConnection()

class UserVehicleDisplay(QtWidgets.QDialog):
    def __init__(self, db_instance=None, parent=None):
        super().__init__(parent)

        self.db = db_instance or db
        self.setWindowTitle("Users and Vehicles")
        self.resize(1100, 700)

        self.qr_images_user = {}     # store loaded QR images for users
        self.qr_images_vehicle = {}  # store loaded QR images for vehicles

        self.init_ui()
        self.load_data()  # load users and vehicles when window opens

        # copy parent's theme if available
        try:
            if parent:
                self.setStyleSheet(parent.styleSheet())
        except:
            pass

    # ===================================================================
    # UI SETUP
    # ===================================================================
    def init_ui(self):
        main_layout = QtWidgets.QVBoxLayout(self)

        top_layout = QtWidgets.QHBoxLayout()
        main_layout.addLayout(top_layout)

        top_layout.addWidget(QtWidgets.QLabel("Search:"))
        self.search_input = QtWidgets.QLineEdit()
        self.search_input.setFixedWidth(300)
        top_layout.addWidget(self.search_input)

        top_layout.addWidget(QtWidgets.QLabel("Filter by Type:"))
        self.type_filter = QtWidgets.QComboBox()
        self.type_filter.addItems(["All", "Student", "Professor", "Worker", "Parent"])
        top_layout.addWidget(self.type_filter)

        top_layout.addStretch()

        self.tabs = QtWidgets.QTabWidget()
        main_layout.addWidget(self.tabs)

        # ---------------- USERS TAB ----------------
        self.user_tab = QtWidgets.QWidget()
        self.user_layout = QtWidgets.QHBoxLayout(self.user_tab)

        self.user_table = QtWidgets.QTableWidget()
        self.user_table.setColumnCount(9)
        self.user_table.setHorizontalHeaderLabels(
            ["ID", "Type", "Name", "Age", "Address", "Contact",
            "Department", "SR Code", "Work Type"]
        )

        # REMOVE ROW NUMBERS
        self.user_table.verticalHeader().setVisible(False)

        self.user_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.user_layout.addWidget(self.user_table)

        user_right = QtWidgets.QVBoxLayout()

        self.user_qr_label = QtWidgets.QLabel("QR Code")
        self.user_qr_label.setFixedSize(220, 220)
        self.user_qr_label.setAlignment(QtCore.Qt.AlignCenter)
        user_right.addWidget(self.user_qr_label)

        self.update_user_btn = QtWidgets.QPushButton("Update User")
        self.update_user_btn.clicked.connect(self.update_user)
        user_right.addWidget(self.update_user_btn)

        self.delete_user_btn = QtWidgets.QPushButton("Delete User")
        self.delete_user_btn.clicked.connect(self.delete_user)
        user_right.addWidget(self.delete_user_btn)

        user_right.addStretch()
        self.user_layout.addLayout(user_right)

        self.tabs.addTab(self.user_tab, "Users")

        # ---------------- VEHICLES TAB ----------------
        self.vehicle_tab = QtWidgets.QWidget()
        self.vehicle_layout = QtWidgets.QHBoxLayout(self.vehicle_tab)

        self.vehicle_table = QtWidgets.QTableWidget()

        # ADD Vehicle ID column (hidden) + User ID column
        self.vehicle_table.setColumnCount(11)
        self.vehicle_table.setHorizontalHeaderLabels(
            ["Vehicle ID", "User ID", "User Type", "Plate", "License", "Sticker",
             "Color", "Status", "Last Seen", "Owner Name", "Owner Sticker"]
        )
        self.vehicle_table.setColumnHidden(0, True)  # Hide Vehicle ID

        # REMOVE ROW NUMBERS
        self.vehicle_table.verticalHeader().setVisible(False)

        self.vehicle_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.vehicle_layout.addWidget(self.vehicle_table)

        vehicle_right = QtWidgets.QVBoxLayout()

        self.vehicle_qr_label = QtWidgets.QLabel("QR Code")
        self.vehicle_qr_label.setFixedSize(220, 220)
        self.vehicle_qr_label.setAlignment(QtCore.Qt.AlignCenter)
        vehicle_right.addWidget(self.vehicle_qr_label)

        self.vehicle_info_label = QtWidgets.QLabel("")
        self.vehicle_info_label.setAlignment(QtCore.Qt.AlignTop)
        vehicle_right.addWidget(self.vehicle_info_label)

        self.update_vehicle_btn = QtWidgets.QPushButton("Update Vehicle")
        self.update_vehicle_btn.clicked.connect(self.update_vehicle)
        vehicle_right.addWidget(self.update_vehicle_btn)

        self.delete_vehicle_btn = QtWidgets.QPushButton("Delete Vehicle")
        self.delete_vehicle_btn.clicked.connect(self.delete_vehicle)
        vehicle_right.addWidget(self.delete_vehicle_btn)

        vehicle_right.addStretch()
        self.vehicle_layout.addLayout(vehicle_right)

        self.tabs.addTab(self.vehicle_tab, "Vehicles")

        self.search_input.textChanged.connect(self.load_data)
        self.type_filter.currentIndexChanged.connect(self.load_data)

        self.user_table.selectionModel().selectionChanged.connect(self.show_user_qr)
        self.vehicle_table.selectionModel().selectionChanged.connect(self.show_vehicle_info)

    # ===================================================================
    # DATA LOADING
    # ===================================================================
    def load_data(self):
        self.load_users()
        self.load_vehicles()

    def load_users(self):
        self.user_table.setRowCount(0)
        self.qr_images_user.clear()

        all_users = self.db.fetch("SELECT * FROM register ORDER BY id")
        search = self.search_input.text().lower()
        filter_type = self.type_filter.currentText()

        for u in all_users:

            if filter_type != "All" and u["type"] != filter_type:
                continue

            searchable = (str(u["id"]) + (u["name"] or "")).lower()
            if search and search not in searchable:
                continue

            row = self.user_table.rowCount()
            self.user_table.insertRow(row)

            data = [
                u["id"], u["type"], u["name"], u["age"], u["address"],
                u["contact_number"], u["department"], u["sr_code"], u["work_type"]
            ]

            for i, val in enumerate(data):
                self.user_table.setItem(row, i, QtWidgets.QTableWidgetItem(str(val or "")))

            if u["qr_file"] and os.path.exists(u["qr_file"]):
                pix = QtGui.QPixmap(u["qr_file"]).scaled(220, 220, QtCore.Qt.KeepAspectRatio)
                self.qr_images_user[u["id"]] = pix

        if self.user_table.rowCount() > 0:
            self.user_table.selectRow(0)
            self.show_user_qr()

    def load_vehicles(self):
        self.vehicle_table.setRowCount(0)
        self.qr_images_vehicle.clear()

        all_v = self.db.fetch("""
            SELECT v.id, r.id AS user_id, r.type AS user_type,
                v.plate, v.license_no, v.sticker_no, v.vcolor,
                v.status, v.last_seen,
                r.name AS owner_name, r.sticker_code AS owner_sticker,
                v.sticker_file
            FROM vehicle v
            LEFT JOIN register r ON v.user_id = r.id
            ORDER BY v.id
        """)

        search = self.search_input.text().lower()

        for v in all_v:
            combo = (str(v["user_id"]) + (v["plate"] or "") +
                    (v["sticker_no"] or "") + (v["owner_name"] or "")).lower()

            if search and search not in combo:
                continue

            row = self.vehicle_table.rowCount()
            self.vehicle_table.insertRow(row)

            data = [
                v["id"], v["user_id"], v["user_type"], v["plate"],
                v["license_no"], v["sticker_no"], v["vcolor"],
                v["status"], v["last_seen"] or "Never",
                v["owner_name"], v["owner_sticker"]
            ]

            for i, val in enumerate(data):
                self.vehicle_table.setItem(row, i, QtWidgets.QTableWidgetItem(str(val or "")))

            # FIX: Use VEHICLE ID for QR
            if v["sticker_file"] and os.path.exists(v["sticker_file"]):
                pix = QtGui.QPixmap(v["sticker_file"]).scaled(220, 220, QtCore.Qt.KeepAspectRatio)
                self.qr_images_vehicle[v["id"]] = pix

        if self.vehicle_table.rowCount() > 0:
            self.vehicle_table.selectRow(0)
            self.show_vehicle_info()

    # ===================================================================
    # DISPLAY FUNCTIONS
    # ===================================================================
    def show_user_qr(self):
        row = self.user_table.currentRow()
        if row < 0:
            return

        uid = int(self.user_table.item(row, 0).text())
        pix = self.qr_images_user.get(uid)

        if pix:
            self.user_qr_label.setPixmap(pix)
        else:
            self.user_qr_label.setText("No QR")

    def show_vehicle_info(self):
        row = self.vehicle_table.currentRow()
        if row < 0:
            return

        # FIX: Load QR using VEHICLE ID (column 0)
        vid = int(self.vehicle_table.item(row, 0).text())
        pix = self.qr_images_vehicle.get(vid)

        if pix:
            self.vehicle_qr_label.setPixmap(pix)
        else:
            self.vehicle_qr_label.setText("No QR")

        values = [self.vehicle_table.item(row, i).text() for i in range(self.vehicle_table.columnCount())]

        self.vehicle_info_label.setText(
            f"Vehicle ID: {values[0]}\n"
            f"User ID: {values[1]}\n"
            f"Type: {values[2]}\n"
            f"Plate: {values[3]}\n"
            f"License: {values[4]}\n"
            f"Sticker: {values[5]}\n"
            f"Color: {values[6]}\n"
            f"Status: {values[7]}\n"
            f"Last Seen: {values[8]}\n"
            f"Owner: {values[9]}\n"
            f"Owner Sticker: {values[10]}"
        )

    # ===================================================================
    # ACTIONS
    # ===================================================================
    def delete_user(self):
        row = self.user_table.currentRow()
        if row < 0:
            return

        uid = int(self.user_table.item(row, 0).text())

        if QtWidgets.QMessageBox.question(self, "Delete User",
                                          "Deleting this user will also delete their vehicles. Continue?") \
                == QtWidgets.QMessageBox.Yes:

            self.db.delete("DELETE FROM vehicle WHERE user_id=?", (uid,))
            self.db.delete("DELETE FROM register WHERE id=?", (uid,))

            self.load_data()

    def update_user(self):
        row = self.user_table.currentRow()
        if row < 0:
            return

        uid = int(self.user_table.item(row, 0).text())

        user = self.db.fetch_one("SELECT * FROM register WHERE id=?", (uid,))
        if not user:
            return

        dlg = QtWidgets.QDialog(self)
        dlg.setWindowTitle("Update User")
        form = QtWidgets.QFormLayout(dlg)

        name = QtWidgets.QLineEdit(user["name"])
        age = QtWidgets.QLineEdit(str(user["age"]))
        address = QtWidgets.QLineEdit(user["address"])
        contact = QtWidgets.QLineEdit(user["contact_number"])
        dept = QtWidgets.QLineEdit(user["department"])
        sr_code = QtWidgets.QLineEdit(user["sr_code"])
        work = QtWidgets.QLineEdit(user["work_type"])

        form.addRow("Name:", name)
        form.addRow("Age:", age)
        form.addRow("Address:", address)
        form.addRow("Contact:", contact)
        form.addRow("Department:", dept)
        form.addRow("SR Code:", sr_code)
        form.addRow("Work Type:", work)

        buttons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok |
                                             QtWidgets.QDialogButtonBox.Cancel)
        form.addRow(buttons)

        buttons.accepted.connect(dlg.accept)
        buttons.rejected.connect(dlg.reject)

        if dlg.exec_() == QtWidgets.QDialog.Accepted:

            self.db.update("""
                UPDATE register 
                SET name=?, age=?, address=?, contact_number=?, department=?, sr_code=?, work_type=? 
                WHERE id=?
            """, (
                name.text(), age.text(), address.text(), contact.text(),
                dept.text(), sr_code.text(), work.text(), uid
            ))

            self.load_data()

    def delete_vehicle(self):
        row = self.vehicle_table.currentRow()
        if row < 0:
            return

        # FIX: delete by VEHICLE ID
        vid = int(self.vehicle_table.item(row, 0).text())

        if QtWidgets.QMessageBox.question(self, "Delete Vehicle", "Confirm delete?") \
                == QtWidgets.QMessageBox.Yes:

            self.db.delete("DELETE FROM vehicle WHERE id=?", (vid,))
            self.load_data()

    def update_vehicle(self):
        row = self.vehicle_table.currentRow()
        if row < 0:
            return

        # FIX: update by VEHICLE ID
        vid = int(self.vehicle_table.item(row, 0).text())

        v = self.db.fetch_one("SELECT * FROM vehicle WHERE id=?", (vid,))
        if not v:
            return

        dlg = QtWidgets.QDialog(self)
        dlg.setWindowTitle("Update Vehicle")
        form = QtWidgets.QFormLayout(dlg)

        plate = QtWidgets.QLineEdit(v["plate"])
        license_no = QtWidgets.QLineEdit(v["license_no"])
        sticker_no = QtWidgets.QLineEdit(v["sticker_no"])
        vcolor = QtWidgets.QLineEdit(v["vcolor"])
        status = QtWidgets.QLineEdit(v["status"])

        form.addRow("Plate Number:", plate)
        form.addRow("License Number:", license_no)
        form.addRow("Sticker Number:", sticker_no)
        form.addRow("Color:", vcolor)
        form.addRow("Status:", status)

        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        form.addRow(buttons)

        buttons.accepted.connect(dlg.accept)
        buttons.rejected.connect(dlg.reject)

        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            self.db.update("""
                UPDATE vehicle
                SET plate=?, license_no=?, sticker_no=?, vcolor=?, status=?
                WHERE id=?
            """, (plate.text(), license_no.text(), sticker_no.text(),
                vcolor.text(), status.text(), vid))

            self.load_data()
