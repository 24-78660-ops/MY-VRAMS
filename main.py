
import sys
import traceback
import hashlib
from datetime import datetime
from PyQt5 import QtWidgets, QtCore

# --- global exception hook (show hidden Qt errors in terminal) ---
def qt_excepthook(exctype, value, tb):
    print("=== Uncaught exception ===")
    traceback.print_exception(exctype, value, tb)
    print("==========================")
sys.excepthook = qt_excepthook

# --- optional GUI modules (allowed to be missing) ---
try:
    from register_gui import RegisterForm
except Exception as e:
    RegisterForm = None
    print("register_gui import failed:", e)

try:
    from user_display import UserVehicleDisplay
except Exception as e:
    UserVehicleDisplay = None
    print("user_display import failed:", e)

try:
    from vehicle_gui import VehicleForm
except Exception as e:
    VehicleForm = None
    print("vehicle_gui import failed:", e)

try:
    from vehicle_monitor import VehicleMonitor
except Exception as e:
    VehicleMonitor = None
    print("vehicle_monitor import failed:", e)

try:
    import charts_gui as charts_gui
except Exception as e:
    charts_gui = None
    print("charts_gui import failed:", e)

from db_con import DBConnection
db = DBConnection()

# ---------- Main Window (Sidebar + Content) ----------
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, admin_user=None):
        super().__init__()
        self.admin_user = admin_user
        self.setWindowTitle("Vehicle Registration System")
        self.resize(1200, 800)
        self.child_windows = {}
        self._init_exception_logger()
        self.init_ui()
        self.load_stylesheet()

    def _init_exception_logger(self):
        pass

    def load_stylesheet(self):
        qss = """
        /* ===== Global ===== */
        QWidget {
            background-color: #0f1724;
            color: #e8eef4;
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 10.5pt;
        }

        QDialog, QMainWindow, QFrame, QGroupBox {
            background-color: #0f1724;
            color: #e8eef4;
        }

        QLabel {
            color: #e8eef4;
        }

        QTableWidget {
            background-color: #0a1a2a;
            color: #e8eef4;
            gridline-color: #274863;
            border: 1px solid #123147;
            selection-background-color: #17527a;
        }

        QHeaderView::section {
            background-color: #0d1a2c;
            color: #e8eef4;
            border: 1px solid #1d3a55;
        }

        /* -------- FIX LISTS (Vehicle Monitor) -------- */
        QListWidget {
            background-color: #0a1a2a;
            border: 1px solid #123147;
            border-radius: 10px;
            padding: 6px;
            color: #d3eaff;
        }

        QListWidget::item {
            padding: 8px;
        }

        QListWidget::item:hover {
            background-color: #13334d;
        }

        QListWidget::item:selected {
            background-color: #0f4a6b;
            color: white;
        }

        /* Smooth animations */
        * {
            transition: all 140ms ease-in-out;
        }

        /* ===== Sidebar ===== */
        QFrame#sidebar {
            background-color: #0b1220;
            border-right: 1px solid #16263a;
        }

        QLabel#brand {
            color: #00d0ff;
            font-weight: 700;
            font-size: 19pt;
            letter-spacing: 0.5px;
        }

        QPushButton[sidebar="true"] {
            background: transparent;
            color: #b6cde0;
            text-align: left;
            padding: 12px 20px;
            border: none;
            font-size: 11pt;
            border-radius: 10px;
        }

        QPushButton[sidebar="true"]:hover {
            background-color: #132437;
            color: white;
            padding-left: 24px;
        }

        QPushButton[sidebar="true"][active="true"] {
            background-color: #0c2e42;
            color: #cfffff;
            font-weight: 600;
        }

        /* Cards */
        QFrame.card {
            background-color: #0d1a2c;
            border: 1px solid #1d3a55;
            border-radius: 14px;
            padding: 16px;
        }

        QLabel.card-title {
            font-weight: 700;
            font-size: 13pt;
            color: #d9f8ff;
        }

        QLabel.card-sub {
            font-size: 10.5pt;
            color: #a4cddd;
        }

        /* Buttons */
        QPushButton {
            padding: 9px 14px;
            border-radius: 8px;
            background-color: #11334f;
            color: #dceeff;
        }

        QPushButton:hover {
            background-color: #17527a;
        }

        QPushButton:pressed {
            background-color: #0e3a57;
        }

        /* Inputs */
        QLineEdit {
            background-color: #071b2c;
            border: 1px solid #11324c;
            padding: 10px;
            border-radius: 8px;
            color: #eaf6ff;
        }

        QLineEdit:focus {
            border: 1px solid #00caff;
            background-color: #0a2235;
        }

        /* Separator line */
        QFrame[frameShape="4"] {
            color: #153044;
        }
        
        QTabWidget::pane {
        border: none;
        background: #081725;
        }

        QTabBar::tab {
            background: #0d2438;
            color: #ffffff;
            padding: 6px 20px;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
        }

        QTabBar::tab:selected {
            background: #15375a;
            color: #ffffff;
        }

        QTabBar::tab:hover {
            background: #1c4a75;
        }

        """

        self.setStyleSheet(qss)


    def init_ui(self):
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        root_layout = QtWidgets.QHBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        sidebar = QtWidgets.QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(260)
        sidebar_layout = QtWidgets.QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(20, 20, 20, 20)
        sidebar_layout.setSpacing(12)

        brand = QtWidgets.QLabel("Vehicle System")
        brand.setObjectName("brand")
        sidebar_layout.addWidget(brand)

        user_label = QtWidgets.QLabel(f"Admin: {self.admin_user['username'] if self.admin_user else 'Unknown'}")
        user_label.setStyleSheet("color:#89b6c7; font-size:10pt;")
        sidebar_layout.addWidget(user_label)

        sidebar_layout.addSpacing(6)
        sidebar_layout.addWidget(self._make_divider())

        self.btn_dashboard = QtWidgets.QPushButton("Dashboard"); self._style_sidebar_btn(self.btn_dashboard, active=True)
        self.btn_register = QtWidgets.QPushButton("Register User"); self._style_sidebar_btn(self.btn_register)
        self.btn_view = QtWidgets.QPushButton("View Users & Vehicles"); self._style_sidebar_btn(self.btn_view)
        self.btn_monitor = QtWidgets.QPushButton("Vehicle Monitoring (Scan)"); self._style_sidebar_btn(self.btn_monitor)
        self.btn_charts = QtWidgets.QPushButton("Vehicle Statistics"); self._style_sidebar_btn(self.btn_charts)
        self.btn_manage_admins = QtWidgets.QPushButton("Manage Admins"); self._style_sidebar_btn(self.btn_manage_admins)
        self.btn_exit = QtWidgets.QPushButton("Exit"); self._style_sidebar_btn(self.btn_exit)

        sidebar_layout.addWidget(self.btn_dashboard)
        sidebar_layout.addWidget(self.btn_register)
        sidebar_layout.addWidget(self.btn_view)
        sidebar_layout.addWidget(self.btn_monitor)
        sidebar_layout.addWidget(self.btn_charts)
        sidebar_layout.addWidget(self.btn_manage_admins)
        sidebar_layout.addStretch()
        sidebar_layout.addWidget(self.btn_exit)

        content_frame = QtWidgets.QFrame()
        content_layout = QtWidgets.QVBoxLayout(content_frame)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(12)

        top_bar = QtWidgets.QHBoxLayout()
        self.page_title = QtWidgets.QLabel("Dashboard")
        self.page_title.setStyleSheet("font-size: 16pt; font-weight: 700;")
        top_bar.addWidget(self.page_title)
        top_bar.addStretch()
        last_login = QtWidgets.QLabel(f"Logged in as: {self.admin_user['username'] if self.admin_user else 'admin'}")
        last_login.setStyleSheet("color:#9ecbdc;")
        top_bar.addWidget(last_login)
        content_layout.addLayout(top_bar)

        self.pages = QtWidgets.QStackedWidget()
        self.pages.setStyleSheet("background: transparent;")

        dash = QtWidgets.QWidget()
        dash_layout = QtWidgets.QVBoxLayout(dash)
        dash_layout.setSpacing(12)

        cards_row = QtWidgets.QHBoxLayout()
        cards_row.setSpacing(14)
        cards_row.addWidget(self._make_info_card("Registered Users", self._get_count_registers()))
        cards_row.addWidget(self._make_info_card("Vehicles", self._get_count_vehicles()))
        cards_row.addWidget(self._make_info_card("Last Entry", self._get_last_entry()))
        dash_layout.addLayout(cards_row)

        logs_card = QtWidgets.QFrame()
        logs_card.setObjectName("card")
        logs_layout = QtWidgets.QVBoxLayout(logs_card)
        logs_layout.setSpacing(8)
        logs_title = QtWidgets.QLabel("Recent Entry/Exit Logs"); logs_title.setObjectName("card-title")
        logs_layout.addWidget(logs_title)
        logs_list = QtWidgets.QListWidget()

        logs = self._fetch_recent_logs(limit=8)
        for l in logs:

            name = l["name"] if ("name" in l.keys() and l["name"]) else "Unknown"
            logs_list.addItem(f"{l['timestamp']} - {name} - {l['direction']}")

        logs_layout.addWidget(logs_list)
        dash_layout.addWidget(logs_card)

        self.pages.addWidget(dash)

        for text in [
            "Use 'Register User' from the sidebar to open the registration dialog.",
            "View users and vehicles will open in a separate window.",
            "Vehicle Monitor opens the scanning window.",
            "Charts / Dashboard page (opens separate window if available).",
            "Manage admins from the sidebar button (opens panel)."
        ]:
            page = QtWidgets.QWidget()
            l = QtWidgets.QVBoxLayout(page)
            lbl = QtWidgets.QLabel(text)
            lbl.setWordWrap(True)
            l.addWidget(lbl)
            self.pages.addWidget(page)

        content_layout.addWidget(self.pages)
        root_layout.addWidget(sidebar)
        root_layout.addWidget(content_frame, stretch=1)
        content_frame.setLayout(content_layout)

        self.btn_dashboard.clicked.connect(lambda: self._activate_page(0))
        self.btn_register.clicked.connect(lambda: self._open_register())
        self.btn_view.clicked.connect(self.view_users_vehicles)
        self.btn_monitor.clicked.connect(self.monitor_vehicles)
        self.btn_charts.clicked.connect(self.show_charts_window)
        self.btn_manage_admins.clicked.connect(self.manage_admins)
        self.btn_exit.clicked.connect(QtWidgets.qApp.quit)

        self._activate_page(0)

    # ---------- helper UI builders ----------
    def _style_sidebar_btn(self, btn, active=False):
        btn.setProperty("sidebar", "true")
        btn.setProperty("active", "true" if active else "false")
        btn.setFixedHeight(44)
        # Refresh style
        btn.style().unpolish(btn)
        btn.style().polish(btn)

    def _make_divider(self):
        d = QtWidgets.QFrame()
        d.setFrameShape(QtWidgets.QFrame.HLine)
        d.setFrameShadow(QtWidgets.QFrame.Sunken)
        d.setStyleSheet("color:#122b3a;")
        d.setFixedHeight(2)
        return d

    def _make_info_card(self, title, subtitle):
        card = QtWidgets.QFrame()
        card.setObjectName("card")
        card.setProperty("class", "card")
        layout = QtWidgets.QVBoxLayout(card)
        lbl_title = QtWidgets.QLabel(title); lbl_title.setObjectName("card-title")
        lbl_sub = QtWidgets.QLabel(subtitle); lbl_sub.setObjectName("card-sub")
        layout.addWidget(lbl_title)
        layout.addWidget(lbl_sub)
        return card

    # ---------- data shortcuts ----------
    def _get_count_registers(self):
        try:
            r = db.fetch_one("SELECT COUNT(*) as c FROM register")
            return str(r['c']) if r else "0"
        except Exception as e:
            print("count registers error:", e)
            return "0"

    def _get_count_vehicles(self):
        try:
            r = db.fetch_one("SELECT COUNT(*) as c FROM vehicle")
            return str(r['c']) if r else "0"
        except Exception as e:
            print("count vehicles error:", e)
            return "0"

    def _get_last_entry(self):
        try:
            r = db.fetch_one("SELECT timestamp FROM entry_exit_log ORDER BY timestamp DESC LIMIT 1")
            return r['timestamp'] if r else "N/A"
        except Exception as e:
            print("last entry error:", e)
            return "N/A"

    def _fetch_recent_logs(self, limit=8):
        try:
            rows = db.fetch(f"SELECT e.timestamp, e.direction, r.name FROM entry_exit_log e LEFT JOIN register r ON e.user_id=r.id ORDER BY e.timestamp DESC LIMIT {limit}")
            return rows
        except Exception as e:
            print("fetch logs error:", e)
            return []

    # ---------- page actions ----------
    def _activate_page(self, index):
        try:
            # Switch page safely
            if index < 0 or index >= self.pages.count():
                return
            self.pages.setCurrentIndex(index)

            # Update page title from the page's first label if present (safe)
            try:
                page = self.pages.currentWidget()
                layout = page.layout()
                if layout and layout.count() > 0:
                    w = layout.itemAt(0).widget()
                    if isinstance(w, QtWidgets.QLabel):
                        self.page_title.setText(w.text())
                    else:
                        # keep dashboard title as default for index 0
                        if index == 0:
                            self.page_title.setText("Dashboard")
                        else:
                            self.page_title.setText("Page")
                else:
                    self.page_title.setText("Page")
            except Exception:
                self.page_title.setText("Page")

            # Reset sidebar button styles
            for btn in (self.btn_dashboard, self.btn_register, self.btn_view, self.btn_monitor, self.btn_charts, self.btn_manage_admins, self.btn_exit):
                try:
                    btn.setProperty("active", "false")
                    btn.style().unpolish(btn); btn.style().polish(btn)
                except Exception:
                    pass

            mapping = {0: self.btn_dashboard, 1: self.btn_register, 2: self.btn_view, 3: self.btn_monitor, 4: self.btn_charts, 5: self.btn_manage_admins}
            if index in mapping:
                b = mapping[index]
                if b:
                    b.setProperty("active", "true")
                    b.style().unpolish(b); b.style().polish(b)

        except Exception as e:
            print("PAGE SWITCH ERROR:", e)

    def _open_register(self):
        items = ["Student", "Professor", "Worker", "Parent"]
        user_type, ok = QtWidgets.QInputDialog.getItem(self, "Select User Type", "User Type:", items, 0, False)
        if not (ok and user_type):
            return
        if RegisterForm is None:
            QtWidgets.QMessageBox.warning(self, "Missing Module", "register_gui.py not found.")
            return
        try:
            dlg = RegisterForm(db_instance=db, user_type=user_type, parent=self)
            # ensure dialog has a parent (prevents immediate GC)
            if hasattr(dlg, "exec_"):
                dlg.exec_()
            else:
                dlg.setWindowFlags(QtCore.Qt.Window)
                dlg.show()
                self.child_windows['register'] = dlg
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to open register form:\n{e}")
            traceback.print_exc()

    def view_users_vehicles(self):
        key = 'user_vehicle'
        if key not in self.child_windows:
            if UserVehicleDisplay is None:
                QtWidgets.QMessageBox.warning(self, "Missing Module", "user_display.py not found.")
                return
            try:
                win = UserVehicleDisplay(db_instance=db, parent=self)
                win.setWindowFlags(QtCore.Qt.Window)
                win.resize(1100, 700)
                self.child_windows[key] = win
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"Failed to open Users/Vehicles:\n{e}")
                traceback.print_exc()
                return
        win = self.child_windows[key]
        win.show(); win.raise_(); win.activateWindow()

    def monitor_vehicles(self):
        key = 'vehicle_monitor'
        if key not in self.child_windows:
            if VehicleMonitor is None:
                QtWidgets.QMessageBox.warning(self, "Missing Module", "vehicle_monitor.py not found.")
                return
            try:
                win = VehicleMonitor(db_instance=db, scan_func=self.process_code, parent=self)
                win.setWindowFlags(QtCore.Qt.Window)
                win.resize(1000, 600)
                self.child_windows[key] = win
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"Failed to open Vehicle Monitor:\n{e}")
                traceback.print_exc()
                return
        win = self.child_windows[key]
        win.show(); win.raise_(); win.activateWindow()

    def show_charts_window(self):
        key = 'charts'
        if key not in self.child_windows:
            if charts_gui is None or not hasattr(charts_gui, "ChartsWindow"):
                QtWidgets.QMessageBox.warning(self, "Missing Module", "charts_gui.py not found or has no ChartsWindow.")
                return
            try:
                w = charts_gui.ChartsWindow(db_instance=db, parent=self)
                w.setWindowFlags(QtCore.Qt.Window)
                w.resize(1000, 700)
                self.child_windows[key] = w
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"Failed to open Charts:\n{e}")
                traceback.print_exc()
                return
        win = self.child_windows[key]
        win.show(); win.raise_(); win.activateWindow()

    def manage_admins(self):
        key = 'admin_win'
        if key not in self.child_windows:
            try:
                admin_win = QtWidgets.QWidget(parent=self)
                admin_win.setWindowTitle("Admin Management")
                layout = QtWidgets.QVBoxLayout(admin_win)
                title = QtWidgets.QLabel("Admin Users"); title.setStyleSheet("font-size: 18pt; font-weight:bold;")
                layout.addWidget(title)
                self.admin_list = QtWidgets.QListWidget()
                layout.addWidget(self.admin_list)
                self.refresh_admins()
                username_entry = QtWidgets.QLineEdit(); username_entry.setPlaceholderText("Username")
                password_entry = QtWidgets.QLineEdit(); password_entry.setPlaceholderText("Password"); password_entry.setEchoMode(QtWidgets.QLineEdit.Password)
                layout.addWidget(username_entry); layout.addWidget(password_entry)
                add_btn = QtWidgets.QPushButton("Add Admin"); add_btn.setStyleSheet("background:#1abc9c;color:white;"); add_btn.clicked.connect(lambda: self.add_admin(username_entry, password_entry))
                del_btn = QtWidgets.QPushButton("Delete Selected Admin"); del_btn.setStyleSheet("background:#e74c3c;color:white;"); del_btn.clicked.connect(self.delete_admin)
                reset_btn = QtWidgets.QPushButton("Reset Selected Password"); reset_btn.clicked.connect(self.reset_admin_password)
                layout.addWidget(add_btn); layout.addWidget(del_btn); layout.addWidget(reset_btn)
                admin_win.setWindowFlags(QtCore.Qt.Window)
                admin_win.resize(700, 500)
                self.child_windows[key] = admin_win
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"Failed to create Admin window:\n{e}")
                traceback.print_exc()
                return
        win = self.child_windows[key]
        win.show(); win.raise_(); win.activateWindow()

    def refresh_admins(self):
        try:
            self.admin_list.clear()
            rows = db.fetch("SELECT id, username FROM admin_users ORDER BY id")
            for r in rows:
                self.admin_list.addItem(f"{r['id']} - {r['username']}")
        except Exception as e:
            print("refresh_admins error:", e)

    def add_admin(self, username_entry, password_entry):
        username = username_entry.text().strip(); password = password_entry.text().strip()
        if not username or not password:
            QtWidgets.QMessageBox.warning(self, "Error", "Please enter username and password!"); return
        hashed = hashlib.sha256(password.encode()).hexdigest()
        try:
            db.insert("INSERT INTO admin_users (username, password_hash) VALUES (?,?)", (username, hashed))
            QtWidgets.QMessageBox.information(self, "Success", f"Admin '{username}' created!")
            self.refresh_admins(); username_entry.clear(); password_entry.clear()
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Error", str(e))

    def delete_admin(self):
        if not hasattr(self, "admin_list"):
            QtWidgets.QMessageBox.warning(self, "Error", "Admin list not initialized"); return
        selected = self.admin_list.currentItem()
        if not selected:
            QtWidgets.QMessageBox.warning(self, "Error", "Select an admin to delete!"); return
        admin_id = int(selected.text().split(" - ")[0])
        reply = QtWidgets.QMessageBox.question(self, "Confirm", "Delete selected admin?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            db.delete("DELETE FROM admin_users WHERE id=?", (admin_id,))
            self.refresh_admins()

    def reset_admin_password(self):
        if not hasattr(self, "admin_list"):
            QtWidgets.QMessageBox.warning(self, "Error", "Admin list not initialized"); return
        selected = self.admin_list.currentItem()
        if not selected:
            QtWidgets.QMessageBox.warning(self, "Error", "Select an admin to reset password!"); return
        admin_id = int(selected.text().split(" - ")[0])
        new_pass, ok = QtWidgets.QInputDialog.getText(self, "Reset Password", "Enter new password:")
        if ok and new_pass:
            hashed = hashlib.sha256(new_pass.encode()).hexdigest()
            db.update("UPDATE admin_users SET password_hash=? WHERE id=?", (hashed, admin_id))
            QtWidgets.QMessageBox.information(self, "Success", "Password reset successfully!")

    def process_code(self, code, refresh_callback=None):
        code = code.strip().upper()
        if not code:
            return
        user = db.fetch_one("SELECT id, name FROM register WHERE sticker_code=?", (code,))
        if not user:
            QtWidgets.QMessageBox.warning(self, "Error", f"Sticker code '{code}' not registered!")
            return
        user_id = user['id']; name = user['name']
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        last_log = db.fetch_one("SELECT direction FROM entry_exit_log WHERE user_id=? ORDER BY timestamp DESC LIMIT 1", (user_id,))
        direction = "IN" if not last_log or last_log['direction'] == "OUT" else "OUT"
        try:
            db.insert("INSERT INTO entry_exit_log (user_id, sticker_code, timestamp, direction) VALUES (?,?,?,?)", (user_id, code, now, direction))
            db.update("UPDATE vehicle SET last_seen=? WHERE user_id=?", (now, user_id))
            QtWidgets.QMessageBox.information(self, "Success", f"{name} logged {direction} at {now}")
            if callable(refresh_callback):
                try:
                    refresh_callback()
                except Exception:
                    pass
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "DB Error", str(e))

# ---------- Login Window ----------
class LoginWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("System Login")
        self.resize(1000, 640)
        self.setStyleSheet("")  # main stylesheet applied in MainWindow
        self.init_ui()
        self.create_default_admin()

    def init_ui(self):
        main_layout = QtWidgets.QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        left = QtWidgets.QFrame()
        left.setFixedWidth(460)
        left_layout = QtWidgets.QVBoxLayout(left)
        left_layout.setContentsMargins(40, 40, 40, 40)
        left_layout.setSpacing(12)
        left.setStyleSheet("background-color: #071328;")

        logo = QtWidgets.QLabel("Vehicle System")
        logo.setStyleSheet("font-size:28pt; color:#00c9ff; font-weight:700;")
        left_layout.addWidget(logo)
        left_layout.addSpacing(8)

        subtitle = QtWidgets.QLabel("Welcome back — please login to continue")
        subtitle.setStyleSheet("color:#9ecfdc; font-size:10pt;")
        left_layout.addWidget(subtitle)
        left_layout.addSpacing(18)

        card = QtWidgets.QFrame()
        card.setStyleSheet("""
            QFrame { background: #0b1b2b; border-radius: 14px; padding: 22px; }
            QLineEdit { background:#071b2c; border:1px solid #123045; padding:10px; border-radius:8px; color:#e6eef5; }
            QLineEdit:focus { border:1px solid #00c9ff; }
            QPushButton#login { background:#00c9ff; color:#071328; padding:10px; border-radius:10px; font-weight:700; }
            QPushButton#login:hover { background:#3ee9ff; }
            QCheckBox { color:#bcdfe9; }
        """)
        card_layout = QtWidgets.QVBoxLayout(card)
        card_layout.setSpacing(12)

        self.username_entry = QtWidgets.QLineEdit()
        self.username_entry.setPlaceholderText("Username")
        card_layout.addWidget(self.username_entry)

        self.password_entry = QtWidgets.QLineEdit()
        self.password_entry.setPlaceholderText("Password")
        self.password_entry.setEchoMode(QtWidgets.QLineEdit.Password)
        card_layout.addWidget(self.password_entry)

        show_cb = QtWidgets.QCheckBox("Show Password")
        show_cb.stateChanged.connect(lambda s: self.password_entry.setEchoMode(QtWidgets.QLineEdit.Normal if s else QtWidgets.QLineEdit.Password))
        card_layout.addWidget(show_cb)

        login_btn = QtWidgets.QPushButton("Login")
        login_btn.setObjectName("login")
        login_btn.clicked.connect(self.authenticate)
        card_layout.addWidget(login_btn)

        left_layout.addWidget(card)
        left_layout.addStretch()

        right = QtWidgets.QFrame()
        right_layout = QtWidgets.QVBoxLayout(right)
        right.setStyleSheet("background-color: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #07223a, stop:1 #0b2540);")

        deco_card = QtWidgets.QFrame()
        deco_card.setStyleSheet("background:transparent; border:none;")
        deco_layout = QtWidgets.QVBoxLayout(deco_card)
        big = QtWidgets.QLabel("Smart Vehicle Dashboard")
        big.setStyleSheet("font-size:22pt; color:#bfefff; font-weight:700;")
        deco_layout.addWidget(big)
        deco_layout.addSpacing(6)
        info = QtWidgets.QLabel("Manage registrations, monitor vehicles, and view analytics.")
        info.setStyleSheet("color:#9dbecb;")
        deco_layout.addWidget(info)
        deco_layout.addStretch()
        right_layout.addWidget(deco_card)
        right_layout.addStretch()

        main_layout.addWidget(left)
        main_layout.addWidget(right)

    def create_default_admin(self):
        admin = db.fetch_one("SELECT id FROM admin_users LIMIT 1")
        if not admin:
            default_user = "admin"
            default_pass = hashlib.sha256("admin".encode()).hexdigest()
            try:
                db.insert("INSERT INTO admin_users (username, password_hash) VALUES (?,?)", (default_user, default_pass))
                print("Created default admin/admin (please change this).")
            except Exception as e:
                print("create_default_admin error:", e)

    def authenticate(self):
        username = self.username_entry.text().strip(); password = self.password_entry.text().strip()
        if not username or not password:
            QtWidgets.QMessageBox.warning(self, "Error", "Please fill all fields!"); return
        hashed = hashlib.sha256(password.encode()).hexdigest()
        user = db.fetch_one("SELECT * FROM admin_users WHERE username=? AND password_hash=?", (username, hashed))
        if user:
            QtWidgets.QMessageBox.information(self, "Success", "Login Successful!")
            self.close()
            try:
                self.main_win = MainWindow(admin_user=user)
                self.main_win.show()
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"Failed to open main window:\n{e}")
                traceback.print_exc()
        else:
            QtWidgets.QMessageBox.warning(self, "Error", "Invalid Username or Password")
            self.username_entry.clear(); self.password_entry.clear()

# ---------- Run ----------
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    login = LoginWindow()
    login.show()
    sys.exit(app.exec_())
