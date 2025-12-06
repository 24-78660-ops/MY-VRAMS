import unittest

class TestScanner(unittest.TestCase):

    def test_code_normalization(self):
        raw = " stk001 "
        normalized = raw.strip().upper()
        self.assertEqual(normalized, "STK001")

if __name__ == "__main__":
    unittest.main()
