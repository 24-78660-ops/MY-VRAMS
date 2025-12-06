import sys
import os

PROJECT_ROOT = r"C:\Users\DARYL\OneDrive\Desktop\My Rams"
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import unittest
import hashlib

class TestLogin(unittest.TestCase):

    def test_password_hash_is_stable(self):
        password = "admin"
        h1 = hashlib.sha256(password.encode()).hexdigest()
        h2 = hashlib.sha256(password.encode()).hexdigest()
        self.assertEqual(h1, h2)

    def test_password_hash_differs(self):
        p1 = "admin"
        p2 = "admin123"
        h1 = hashlib.sha256(p1.encode()).hexdigest()
        h2 = hashlib.sha256(p2.encode()).hexdigest()
        self.assertNotEqual(h1, h2)

if __name__ == "__main__":
    unittest.main()
