import sys
import os

PROJECT_ROOT = r"C:\Users\DARYL\OneDrive\Desktop\My Rams"
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import unittest
from pathlib import Path
from qr_generator import generate_sticker_code, generate_vehicle_qr

class TestQR(unittest.TestCase):

    def test_sticker_code_format(self):
        code = generate_sticker_code(123)
        # format: YY-000123
        self.assertRegex(code, r"\d{2}-\d{5}")

    def test_vehicle_qr_generation(self):
        sticker, qr_file = generate_vehicle_qr(50)
        self.assertTrue(sticker)
        self.assertTrue(qr_file)
        self.assertTrue(Path(qr_file).exists())

if __name__ == "__main__":
    unittest.main()
