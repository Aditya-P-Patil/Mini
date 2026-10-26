
import math
from typing import Optional


def calculate_margin(
    profit: Optional[float],
    revenue: Optional[float],
) -> Optional[float]:
    """Calculate a profit margin as a percentage."""
    if profit is None or revenue is None:
        return None

    if not math.isfinite(profit) or not math.isfinite(revenue):
        return None

    if revenue <= 0:
        return None

    return round((profit / revenue) * 100, 2)


def calculate_gross_margin(
    gross_profit: Optional[float],
    revenue: Optional[float],
) -> Optional[float]:
    """Gross profit margin percentage."""
    return calculate_margin(gross_profit, revenue)


def calculate_operating_margin(
    operating_income: Optional[float],
    revenue: Optional[float],
) -> Optional[float]:
    """Operating margin percentage."""
    return calculate_margin(operating_income, revenue)


def calculate_net_profit_margin(
    net_income: Optional[float],
    revenue: Optional[float],
) -> Optional[float]:
    """Net profit margin percentage."""
    return calculate_margin(net_income, revenue)
