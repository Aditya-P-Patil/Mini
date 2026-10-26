
from dataclasses import dataclass
from typing import Optional


@dataclass
class FinancialRecord:
    """Standard structure for one company's financial reporting period."""

    company_name: str
    ticker: Optional[str]
    period_end: str

    total_revenue: Optional[float]
    gross_profit: Optional[float]
    operating_income: Optional[float]
    net_income: Optional[float]

    currency: Optional[str] = None
    unit_scale: Optional[float] = None

    source_file: Optional[str] = None
    source_location: Optional[str] = None
