"""
Sprint 2
Cash Flow KPI Engine
"""

def free_cash_flow(cfo, cfi):
    """
    Free Cash Flow
    """
    return round(cfo + cfi, 2)


def cfo_quality_score(cfo, pat):

    if pat == 0:
        return None

    ratio = cfo / pat

    if ratio > 1:
        return "High Quality"

    elif ratio >= 0.5:
        return "Moderate"

    else:
        return "Accrual Risk"


def capex_intensity(cfi, sales):

    if sales == 0:
        return None

    pct = abs(cfi) / sales * 100

    if pct < 3:
        return "Asset Light"

    elif pct <= 8:
        return "Moderate"

    else:
        return "Capital Intensive"


def fcf_conversion_rate(fcf, operating_profit):

    if operating_profit == 0:
        return None

    return round(
        (fcf / operating_profit) * 100,
        2
    )


def capital_allocation_pattern(cfo, cfi, cff, quality=None):

    signs = (
        "+" if cfo >= 0 else "-",
        "+" if cfi >= 0 else "-",
        "+" if cff >= 0 else "-"
    )

    if signs == ("+", "-", "-"):

        if quality == "High Quality":
            return "Shareholder Returns"

        return "Reinvestor"

    if signs == ("+", "+", "-"):
        return "Liquidating Assets"

    if signs == ("-", "+", "+"):
        return "Distress Signal"

    if signs == ("-", "-", "+"):
        return "Growth Funded by Debt"

    if signs == ("+", "+", "+"):
        return "Cash Accumulator"

    if signs == ("-", "-", "-"):
        return "Pre-Revenue"

    if signs == ("+", "-", "+"):
        return "Mixed"

    return "Other"