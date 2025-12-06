from PyQt5 import QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import numpy as np
import calendar
from db_con import DBConnection

db = DBConnection()

class ChartsWindow(QtWidgets.QWidget):
    def __init__(self, db_instance=None, parent=None):
        super().__init__(parent)
        self.db = db_instance or db
        self.setWindowTitle("Vehicle Statistics Dashboard")
        self.resize(1000, 700)
        self.init_ui()
        self.update_charts()

    def init_ui(self):
        layout = QtWidgets.QVBoxLayout(self)

        self.fig_week, self.ax_week = plt.subplots(figsize=(8,3))
        self.canvas_week = FigureCanvas(self.fig_week)
        layout.addWidget(self.canvas_week)

        self.fig_total, self.ax_total = plt.subplots(figsize=(6,3))
        self.canvas_total = FigureCanvas(self.fig_total)
        layout.addWidget(self.canvas_total)

        btn_layout = QtWidgets.QHBoxLayout()
        refresh = QtWidgets.QPushButton("Refresh Charts"); refresh.clicked.connect(self.update_charts)
        btn_layout.addWidget(refresh)
        layout.addLayout(btn_layout)

    def update_charts(self):
        vehicle_types = [r['vtype'] for r in self.db.fetch("SELECT DISTINCT vtype FROM vehicle WHERE vtype IS NOT NULL")]
        if not vehicle_types:
            vehicle_types = ["Car", "Motorcycle", "Truck", "Van"]

        self.ax_week.clear()
        x = np.arange(7)
        width = 0.8 / max(1, len(vehicle_types))
        for i, vtype in enumerate(vehicle_types):
            rows = self.db.fetch("""
                SELECT strftime('%w', timestamp) as dow, COUNT(*) as cnt
                FROM entry_exit_log l
                JOIN vehicle v ON v.sticker_no = l.sticker_code
                WHERE v.vtype = ?
                GROUP BY dow
            """, (vtype,))
            counts = [0]*7
            for r in rows:
                idx = int(r['dow'])
                counts[idx] = r['cnt']
            self.ax_week.bar(x + i*width, counts, width, label=vtype)
        self.ax_week.set_xticks(x)
        self.ax_week.set_xticklabels(list(calendar.day_name))
        self.ax_week.set_ylabel("Entries")
        self.ax_week.set_title("Weekly Vehicle Entries by Type")
        self.ax_week.legend()
        self.canvas_week.draw()

        self.ax_total.clear()
        totals = []
        for vtype in vehicle_types:
            row = self.db.fetch_one("SELECT COUNT(*) as c FROM vehicle WHERE vtype=?", (vtype,))
            totals.append(row['c'] if row else 0)
        self.ax_total.bar(vehicle_types, totals)
        self.ax_total.set_title("Total Registered Vehicles by Type")
        self.canvas_total.draw()

def show_charts(db_instance=None):
    w = ChartsWindow(db_instance=db_instance)
    w.show()
    return w
