
def net_profit_margin(net_profit, sales):
    """
    Net Profit Margin = (Net Profit / Sales) × 100
    Returns None if sales is zero or missing.
    """
    if sales is None or sales == 0:
        return None

    return round((net_profit / sales) * 100, 2)


def operating_profit_margin(operating_profit, sales):
    """
    Operating Profit Margin = (Operating Profit / Sales) × 100
    Returns None if sales is zero or missing.
    """
    if sales is None or sales == 0:
        return None

    return round((operating_profit / sales) * 100, 2)


def return_on_equity(net_profit, equity_capital, reserves):
    """
    ROE = Net Profit / (Equity Capital + Reserves) × 100

    Return None if equity + reserves <= 0
    """

    equity = equity_capital + reserves

    if equity <= 0:
        return None

    return round((net_profit / equity) * 100, 2)


def return_on_capital_employed(ebit, equity_capital, reserves, borrowings):
    """
    ROCE = EBIT / (Equity + Reserves + Borrowings) × 100

    Return None if denominator <= 0
    """

    capital = equity_capital + reserves + borrowings

    if capital <= 0:
        return None

    return round((ebit / capital) * 100, 2)


def return_on_assets(net_profit, total_assets):
    """
    ROA = Net Profit / Total Assets × 100

    Return None if total_assets <= 0
    """

    if total_assets <= 0:
        return None

    return round((net_profit / total_assets) * 100, 2)

def debt_to_equity(borrowings, equity_capital, reserves):
    """
    Debt-to-Equity = Borrowings / (Equity + Reserves)

    Rules:
    - Return 0 if borrowings = 0
    - Return None if equity + reserves <= 0
    """

    if borrowings == 0:
        return 0

    equity = equity_capital + reserves

    if equity <= 0:
        return None

    return round(borrowings / equity, 2)


def high_leverage_flag(debt_equity_ratio, sector):
    """
    High leverage if:
    D/E > 5 AND sector is not Financials
    """

    if debt_equity_ratio is None:
        return False

    if sector == "Financials":
        return False

    return debt_equity_ratio > 5


def interest_coverage_ratio(operating_profit, other_income, interest):
    """
    Interest Coverage Ratio

    (Operating Profit + Other Income) / Interest

    Return None if interest = 0
    """

    if interest == 0:
        return None

    return round((operating_profit + other_income) / interest, 2)


def icr_label(interest):
    """
    Debt-free companies
    """

    if interest == 0:
        return "Debt Free"

    return None


def icr_warning(icr):
    """
    Warning if ICR < 1.5
    """

    if icr is None:
        return False

    return icr < 1.5


def net_debt(borrowings, investments):
    """
    Net Debt = Borrowings - Investments
    """

    return round(borrowings - investments, 2)


def asset_turnover(sales, total_assets):
    """
    Asset Turnover = Sales / Total Assets
    """

    if total_assets <= 0:
        return None

    return round(sales / total_assets, 2)