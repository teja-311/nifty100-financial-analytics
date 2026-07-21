import unittest
from src.analytics.cagr import calculate_cagr

class TestCAGR(unittest.TestCase):

    def test_normal(self):
        value, flag = calculate_cagr(100, 150, 5)

        self.assertEqual(value, 8.45)
        self.assertEqual(flag, "OK")

    def test_decline_to_loss(self):
        value, flag = calculate_cagr(100, -50, 5)

        self.assertIsNone(value)
        self.assertEqual(flag, "DECLINE_TO_LOSS")

    def test_turnaround(self):
        value, flag = calculate_cagr(-100, 50, 5)

        self.assertIsNone(value)
        self.assertEqual(flag, "TURNAROUND")

    def test_both_negative(self):
        value, flag = calculate_cagr(-100, -50, 5)

        self.assertIsNone(value)
        self.assertEqual(flag, "BOTH_NEGATIVE")

    def test_zero_base(self):
        value, flag = calculate_cagr(0, 50, 5)

        self.assertIsNone(value)
        self.assertEqual(flag, "ZERO_BASE")

    def test_insufficient(self):
        value, flag = calculate_cagr(100, 150, 0)

        self.assertIsNone(value)
        self.assertEqual(flag, "INSUFFICIENT")

    def test_negative_growth(self):
        value, flag = calculate_cagr(150, 100, 5)

        self.assertLess(value, 0)
        self.assertEqual(flag, "OK")

    def test_same_value(self):
        value, flag = calculate_cagr(100, 100, 5)

        self.assertEqual(value, 0)
        self.assertEqual(flag, "OK")

    def test_large_growth(self):
        value, flag = calculate_cagr(100, 1000, 10)

        self.assertGreater(value, 0)
        self.assertEqual(flag, "OK")

    def test_short_period(self):
        value, flag = calculate_cagr(100, 120, 1)

        self.assertEqual(value, 20)
        self.assertEqual(flag, "OK")


if __name__ == "__main__":
    unittest.main()