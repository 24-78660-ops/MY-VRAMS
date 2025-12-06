from PyQt5 import QtWidgets, QtCore
import threading
import re
from db_con import DBConnection

db = DBConnection()
_STICKER_RE = re.compile(r"[A-Z0-9-]{3,}")

def extract_sticker_code_from_raw(raw):
    if not raw:
        return None
    text = raw.strip()

    try:
        import json
        j = json.loads(text)
        for key in ("sticker_code", "code", "sticker"):
            if key in j and isinstance(j[key], str) and j[key].strip():
                return j[key].strip().upper()
    except Exception:
        pass

    m = re.search(r'(sticker_code|code|sticker)\s*[:=]\s*([A-Za-z0-9\-]+)', text, flags=re.IGNORECASE)
    if m:
        return m.group(2).strip().upper()

    m = re.search(r'[?&](sticker_code|code)=([A-Za-z0-9\-]+)', text, flags=re.IGNORECASE)
    if m:
        return m.group(2).strip().upper()

    m = _STICKER_RE.search(text.upper())
    if m:
        return m.group(0)

    return None

class VehicleMonitor(QtWidgets.QWidget):
    code_scanned = QtCore.pyqtSignal(str)

    def __init__(self, db_instance=None, scan_func=None, parent=None):
        super().__init__(parent)

        # simple comment: this whole class handles scanning sticker codes,
        # checking the database, logging vehicle IN/OUT, and showing the log table
        self.db = db_instance or db
        self.scan_func = scan_func
        self._scanner_thread = None
        self._scanner_running = False
        self.setWindowTitle("Vehicle Monitoring / Logbook")
        self.resize(1000, 600)
        self.init_ui()
        self.code_scanned.connect(self._on_code_scanned_main_thread)
        self.refresh_table()

    def init_ui(self):
        layout = QtWidgets.QVBoxLayout(self)

        title = QtWidgets.QLabel("VEHICLE ENTRY/EXIT LOGBOOK")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet("font-size: 16pt; font-weight: bold; padding:8px;")
        layout.addWidget(title)

        filter_layout = QtWidgets.QHBoxLayout()
        filter_layout.addWidget(QtWidgets.QLabel("Filter by Date (YYYY-MM-DD):"))
        self.date_entry = QtWidgets.QLineEdit()
        self.date_entry.setFixedWidth(150)
        self.date_entry.returnPressed.connect(self.refresh_table)
        filter_layout.addWidget(self.date_entry)
        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        scan_layout = QtWidgets.QHBoxLayout()
        self.scan_entry = QtWidgets.QLineEdit()
        self.scan_entry.setPlaceholderText("Scan sticker (USB keyboard scanner) or paste text then press Enter")
        self.scan_entry.returnPressed.connect(self.on_scan_entered)
        scan_layout.addWidget(self.scan_entry)

        clear_btn = QtWidgets.QPushButton("Clear")
        clear_btn.clicked.connect(lambda: self.scan_entry.clear())
        scan_layout.addWidget(clear_btn)

        self.scan_choice_btn = QtWidgets.QPushButton("Scan Vehicle")
        self.scan_choice_btn.clicked.connect(self.open_scan_choice)
        scan_layout.addWidget(self.scan_choice_btn)

        layout.addLayout(scan_layout)

        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "User Name", "Sticker Code", "Plate", "Direction", "Timestamp"])
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        layout.addWidget(self.table)

        btn_layout = QtWidgets.QHBoxLayout()
        refresh_btn = QtWidgets.QPushButton("Refresh Table")
        refresh_btn.clicked.connect(self.refresh_table)
        btn_layout.addWidget(refresh_btn)

        start_cam_btn = QtWidgets.QPushButton("Start Camera Scanner (background)")
        start_cam_btn.clicked.connect(self.start_camera_in_background)
        btn_layout.addWidget(start_cam_btn)

        stop_cam_btn = QtWidgets.QPushButton("Stop Camera Scanner")
        stop_cam_btn.clicked.connect(self.stop_camera_scanner)
        btn_layout.addWidget(stop_cam_btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

    def refresh_table(self):
        self.table.setRowCount(0)
        date_filter = self.date_entry.text().strip()
        if date_filter:
            logs = self.db.fetch("""
                SELECT e.id, r.name, e.sticker_code, v.plate, e.direction, e.timestamp
                FROM entry_exit_log e
                JOIN register r ON e.user_id = r.id
                LEFT JOIN vehicle v ON v.user_id = r.id
                WHERE date(e.timestamp) = ?
                ORDER BY e.timestamp DESC
            """, (date_filter,))
        else:
            logs = self.db.fetch("""
                SELECT e.id, r.name, e.sticker_code, v.plate, e.direction, e.timestamp
                FROM entry_exit_log e
                JOIN register r ON e.user_id = r.id
                LEFT JOIN vehicle v ON v.user_id = r.id
                ORDER BY e.timestamp DESC
            """)

        self.table.setRowCount(len(logs))
        for row_idx, log in enumerate(logs):
            for col_idx, val in enumerate(log):
                item = QtWidgets.QTableWidgetItem(str(val))
                item.setTextAlignment(QtCore.Qt.AlignCenter)
                self.table.setItem(row_idx, col_idx, item)

    def on_scan_entered(self):
        raw = self.scan_entry.text()
        self.scan_entry.clear()
        if not raw:
            return
        code = extract_sticker_code_from_raw(raw)
        if not code:
            QtWidgets.QMessageBox.warning(self, "Invalid", "No valid sticker code found in input.")
            return
        self._dispatch_code(code)

    def open_scan_choice(self):
        dlg = QtWidgets.QMessageBox(self)
        dlg.setWindowTitle("Choose Scan Method")
        dlg.setText("Choose scan method for vehicle:")
        cam_btn = dlg.addButton("Camera Scanner", QtWidgets.QMessageBox.AcceptRole)
        manual_btn = dlg.addButton("Manual Entry", QtWidgets.QMessageBox.RejectRole)
        dlg.exec_()
        if dlg.clickedButton() == cam_btn:
            self.start_camera_in_background()
        elif dlg.clickedButton() == manual_btn:
            code, ok = QtWidgets.QInputDialog.getText(self, "Manual Sticker Entry", "Type sticker code:")
            if ok and code:
                code = extract_sticker_code_from_raw(code)
                if not code:
                    QtWidgets.QMessageBox.warning(self, "Invalid", "No valid sticker code found in input.")
                    return
                self._dispatch_code(code)

    def _dispatch_code(self, code):
        if not code:
            return
        if callable(self.scan_func):
            try:
                self.scan_func(code, refresh_callback=self.refresh_table)
                return
            except Exception:
                pass
        self._process_code_local(code)

    def _process_code_local(self, code):
        user = self.db.fetch_one("SELECT id, name FROM register WHERE sticker_code=?", (code,))
        if not user:
            QtWidgets.QMessageBox.warning(self, "Error", "Sticker code not registered!")
            return

        user_id = user['id']
        name = user['name']

        from datetime import datetime
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        last_log = self.db.fetch_one(
            "SELECT direction FROM entry_exit_log WHERE user_id=? ORDER BY timestamp DESC LIMIT 1", 
            (user_id,)
        )

        direction = "IN" if not last_log or last_log['direction'] == "OUT" else "OUT"

        self.db.insert(
            "INSERT INTO entry_exit_log (user_id, sticker_code, timestamp, direction) VALUES (?,?,?,?)",
            (user_id, code, now, direction)
        )

        self.db.update("UPDATE vehicle SET last_seen=? WHERE user_id=?", (now, user_id))

        QtWidgets.QMessageBox.information(self, "Success", f"{name} logged {direction} at {now}")
        self.refresh_table()

    def start_camera_in_background(self):
        if self._scanner_running:
            QtWidgets.QMessageBox.information(self, "Scanner", "Camera scanner already running.")
            return
        try:
            import scanner as scanner_mod
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Scanner Missing", f"scanner.py import failed: {e}")
            return

        def thread_callback(raw_text):
            code = extract_sticker_code_from_raw(raw_text or "")
            if code:
                try:
                    self.code_scanned.emit(code)
                except Exception:
                    pass

        def worker():
            self._scanner_running = True
            try:
                scanner_mod.start_camera_scanner(thread_callback)
            except Exception as e:
                try:
                    self.code_scanned.emit("__SCANNER_ERROR__::" + str(e))
                except Exception:
                    pass
            finally:
                self._scanner_running = False

        t = threading.Thread(target=worker, daemon=True)
        t.start()
        self._scanner_thread = t
        QtWidgets.QMessageBox.information(self, "Scanner", "Camera scanner started. Focus scanner window and press 'q' to stop.")

    def stop_camera_scanner(self):
        if not self._scanner_running:
            QtWidgets.QMessageBox.information(self, "Scanner", "Camera scanner is not running.")
        else:
            QtWidgets.QMessageBox.information(self, "Scanner", "To stop scanner, focus scanner window and press 'q'.")

    @QtCore.pyqtSlot(str)
    def _on_code_scanned_main_thread(self, code):
        if not code:
            return
        if code.startswith("__SCANNER_ERROR__::"):
            err = code.split("::", 1)[1]
            QtWidgets.QMessageBox.warning(self, "Scanner Error", err)
            return
        self._dispatch_code(code)
