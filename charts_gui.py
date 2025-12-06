from PyQt5 import QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import numpy as np
import calendar
from matplotlib.animation import FuncAnimation
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

        # Weekly Chart (Bar Graph)
        self.fig_week, self.ax_week = plt.subplots(figsize=(8, 3))
        self.canvas_week = FigureCanvas(self.fig_week)
        layout.addWidget(self.canvas_week)

        # Total Vehicles Chart (PIE)
        self.fig_total, self.ax_total = plt.subplots(figsize=(6, 3))
        self.canvas_total = FigureCanvas(self.fig_total)
        layout.addWidget(self.canvas_total)

        # Refresh Button
        btn_layout = QtWidgets.QHBoxLayout()
        refresh = QtWidgets.QPushButton("Refresh Charts")
        refresh.clicked.connect(self.update_charts)
        btn_layout.addWidget(refresh)
        layout.addLayout(btn_layout)

    def update_charts(self):
        # =========================================
        # --- WEEKLY BAR CHART (Mon–Sun monitored logs) ---
        # =========================================

        # Query weekly counts directly
        weekly_totals = [0] * 7  # Mon–Sun

        raw_rows = self.db.fetch("""
            SELECT strftime('%w', timestamp) AS dow, COUNT(*) AS cnt
            FROM entry_exit_log
            GROUP BY dow;
        """)

        # Convert SQLite DOW → Mon-Sun index
        for r in raw_rows:
            raw_dow = int(r["dow"])  
            day_index = (raw_dow - 1) % 7 
            weekly_totals[day_index] = r["cnt"]

        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        x = np.arange(7)

        self.ax_week.clear()
        bars = self.ax_week.bar(x, [0]*7, color="#4aa3ff", width=0.6)

        self.ax_week.set_xticks(x)
        self.ax_week.set_xticklabels(days)
        self.ax_week.set_ylabel("Entries")
        self.ax_week.set_title("Weekly Vehicle Entries (Mon–Sun)")

        # Animate weekly entries
        def animate_week(frame):
            for i in range(7):
                bars[i].set_height(weekly_totals[i] * frame)
            return bars

        FuncAnimation(self.fig_week, animate_week,
                      frames=np.linspace(0, 1, 30), blit=False)
        self.canvas_week.draw()

        # =========================================
        # --- PIE CHART: TOTAL REGISTERED VEHICLES
        # =========================================

        vehicle_types = [
            r["vtype"] for r in self.db.fetch(
                "SELECT DISTINCT vtype FROM vehicle WHERE vtype IS NOT NULL"
            )
        ]

        if not vehicle_types:
            vehicle_types = ["Car", "Motorcycle", "Truck", "Van", "Motor"]

        totals = []
        for vtype in vehicle_types:
            row = self.db.fetch_one(
                "SELECT COUNT(*) AS c FROM vehicle WHERE vtype=?",
                (vtype,)
            )
            totals.append(row["c"] if row else 0)

        self.ax_total.clear()

        # Remove types with zero so pie chart doesn’t break
        filtered = [(t, c) for t, c in zip(vehicle_types, totals) if c > 0]

        if not filtered:
            self.ax_total.text(0.5, 0.5, "No Vehicles Registered",
                               ha="center", va="center", fontsize=14)
            self.canvas_total.draw()
            return

        labels, values = zip(*filtered)

        self.ax_total.pie(
            values,
            labels=labels,
            autopct="%1.1f%%",
            startangle=140
        )

        self.ax_total.set_title("Total Registered Vehicles by Type (Pie Chart)")
        self.canvas_total.draw()


def show_charts(db_instance=None):
    w = ChartsWindow(db_instance=db_instance)
    w.show()
    return w
