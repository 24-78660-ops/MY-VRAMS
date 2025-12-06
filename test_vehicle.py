import sys
import os

PROJECT_ROOT = r"C:\Users\DARYL\OneDrive\Desktop\My Rams"
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import unittest
from db_con import DBConnection
from qr_generator import generate_vehicle_qr

class TestVehicle(unittest.TestCase):

    def setUp(self):
        self.db = DBConnection()
        # Create a temp user
        self.user_id = self.db.insert(
            "INSERT INTO register (name, type) VALUES (?, ?)",
            ("VehicleTestUser", "Student")
        )

    def test_vehicle_insert(self):
        vehicle_id = self.db.insert(
            "INSERT INTO vehicle (user_id, vtype, plate, license_no, vcolor, status) VALUES (?,?,?,?,?,?)",
            (self.user_id, "Car", "UNIT123", "LIC123", "Black", "Active")
        )
        row = self.db.fetch_one("SELECT * FROM vehicle WHERE id=?", (vehicle_id,))
        self.assertIsNotNone(row)
        self.assertEqual(row["plate"], "UNIT123")

    def test_vehicle_qr_link(self):
        vehicle_id = self.db.insert(
            "INSERT INTO vehicle (user_id, vtype, plate, license_no, vcolor, status) VALUES (?,?,?,?,?,?)",
            (self.user_id, "Motorcycle", "QR123", "", "", "Active")
        )
        sticker, qr_file = generate_vehicle_qr(vehicle_id)
        # Save into DB as your app does
        self.db.update(
            "UPDATE vehicle SET sticker_no=?, sticker_file=? WHERE id=?",
            (sticker, qr_file, vehicle_id)
        )
        row = self.db.fetch_one("SELECT sticker_no, sticker_file FROM vehicle WHERE id=?", (vehicle_id,))
        self.assertEqual(row["sticker_no"], sticker)
        self.assertTrue(row["sticker_file"])

if __name__ == "__main__":
    unittest.main()
