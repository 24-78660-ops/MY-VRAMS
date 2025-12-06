import sys
import os

PROJECT_ROOT = r"C:\Users\DARYL\OneDrive\Desktop\My Rams"
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import unittest
from datetime import datetime
from db_con import DBConnection

class TestMonitor(unittest.TestCase):

    def setUp(self):
        self.db = DBConnection()
        self.user_id = self.db.insert(
            "INSERT INTO register (name, type) VALUES (?, ?)",
            ("MonitorUser", "Professor")
        )
        self.vehicle_id = self.db.insert(
            "INSERT INTO vehicle (user_id, vtype, plate, license_no, vcolor, status) VALUES (?,?,?,?,?,?)",
            (self.user_id, "Car", "MON123", "", "", "Active")
        )

    def test_last_seen_updates(self):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.db.update("UPDATE vehicle SET last_seen=? WHERE id=?", (now, self.vehicle_id))
        row = self.db.fetch_one("SELECT last_seen FROM vehicle WHERE id=?", (self.vehicle_id,))
        self.assertEqual(row["last_seen"], now)

if __name__ == "__main__":
    unittest.main()
