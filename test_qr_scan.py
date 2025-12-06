import sys
import os

PROJECT_ROOT = r"C:\Users\DARYL\OneDrive\Desktop\My Rams"
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import unittest

class TestQRScan(unittest.TestCase):

    def test_scanned_string_to_code(self):
        decoded = "25-00001\n"
        code = decoded.strip().upper()
        self.assertEqual(code, "25-00001")

if __name__ == "__main__":
    unittest.main()
