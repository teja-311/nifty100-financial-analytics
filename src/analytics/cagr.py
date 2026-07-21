"""
Sprint 2 - Day 10
CAGR Engine
"""

def calculate_cagr(start_value, end_value, years):
    """
    Calculate CAGR with edge-case handling.

    Returns:
        (cagr_value, flag)
    """

    # Invalid period
    if years <= 0:
        return None, "INSUFFICIENT"

    # Zero base
    if start_value == 0:
        return None, "ZERO_BASE"

    # Positive -> Negative
    if start_value > 0 and end_value < 0:
        return None, "DECLINE_TO_LOSS"

    # Negative -> Positive
    if start_value < 0 and end_value > 0:
        return None, "TURNAROUND"

    # Negative -> Negative
    if start_value < 0 and end_value < 0:
        return None, "BOTH_NEGATIVE"

    # Normal CAGR
    cagr = (((end_value / start_value) ** (1 / years)) - 1) * 100

    return round(cagr, 2), "OK"