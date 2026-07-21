import unittest

from src.analytics.ratios import (
    net_profit_margin,
    operating_profit_margin,
    return_on_equity,
    return_on_capital_employed,
    return_on_assets,
    debt_to_equity,
    high_leverage_flag,
    interest_coverage_ratio,
    icr_label,
    icr_warning,
    net_debt,
    asset_turnover
)

class TestFinancialRatios(unittest.TestCase):

    # Test 1
    def test_net_profit_margin_normal(self):
        self.assertEqual(
            net_profit_margin(100, 1000),
            10.0
        )

    # Test 2
    def test_net_profit_margin_zero_sales(self):
        self.assertIsNone(
            net_profit_margin(100, 0)
        )

    # Test 3
    def test_operating_profit_margin(self):
        self.assertEqual(
            operating_profit_margin(250, 1000),
            25.0
        )

    # Test 4
    def test_roe_normal(self):
        self.assertEqual(
            return_on_equity(120, 400, 200),
            20.0
        )

    # Test 5
    def test_roe_negative_equity(self):
        self.assertIsNone(
            return_on_equity(100, -100, 50)
        )

    # Test 6
    def test_roce_normal(self):
        self.assertEqual(
            return_on_capital_employed(180, 400, 200, 100),
            25.71
        )

    # Test 7
    def test_roce_zero_capital(self):
        self.assertIsNone(
            return_on_capital_employed(100, 0, 0, 0)
        )

    # Test 8
    def test_roa_zero_assets(self):
        self.assertIsNone(
            return_on_assets(100, 0)
        )

    # Test 9   

    def test_debt_to_equity_normal(self):
        self.assertEqual(
            debt_to_equity(300, 400, 200),
            0.5
        )

    def test_debt_to_equity_debt_free(self):
        self.assertEqual(
            debt_to_equity(0, 400, 200),
            0
        )

    def test_high_leverage_flag(self):
        self.assertTrue(
            high_leverage_flag(6.2, "Industrials")
        )

    def test_high_leverage_financials(self):
        self.assertFalse(
            high_leverage_flag(8.5, "Financials")
        )

    def test_interest_coverage_zero_interest(self):
        self.assertIsNone(
            interest_coverage_ratio(200, 20, 0)
        )

    def test_icr_label(self):
        self.assertEqual(
            icr_label(0),
            "Debt Free"
        )

    def test_icr_warning(self):
        self.assertTrue(
            icr_warning(1.2)
        )

    def test_asset_turnover(self):
        self.assertEqual(
            asset_turnover(1200, 600),
            2.0
        )


if __name__ == "__main__":
    unittest.main()