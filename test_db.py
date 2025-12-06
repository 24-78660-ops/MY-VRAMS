import sys
import os

# Ensure project root is on sys.path
PROJECT_ROOT = r"C:\Users\DARYL\OneDrive\Desktop\My Rams"
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import unittest
from db_con import DBConnection

class TestDatabase(unittest.TestCase):

    def setUp(self):
        self.db = DBConnection()

    def test_insert_and_fetch_user(self):
        user_id = self.db.insert(
            "INSERT INTO register (name, type) VALUES (?, ?)",
            ("UnitTest User", "Student")
        )
        row = self.db.fetch_one("SELECT * FROM register WHERE id=?", (user_id,))
        self.assertIsNotNone(row)
        self.assertEqual(row["name"], "UnitTest User")

    def test_update_user(self):
        user_id = self.db.insert(
            "INSERT INTO register (name, type) VALUES (?, ?)",
            ("OldName", "Worker")
        )
        self.db.update("UPDATE register SET name=? WHERE id=?", ("NewName", user_id))
        row = self.db.fetch_one("SELECT name FROM register WHERE id=?", (user_id,))
        self.assertEqual(row["name"], "NewName")

    def test_delete_user(self):
        user_id = self.db.insert(
            "INSERT INTO register (name, type) VALUES (?, ?)",
            ("DeleteMe", "Parent")
        )
        self.db.delete("DELETE FROM register WHERE id=?", (user_id,))
        row = self.db.fetch_one("SELECT * FROM register WHERE id=?", (user_id,))
        self.assertIsNone(row)

if __name__ == "__main__":
    unittest.main()
