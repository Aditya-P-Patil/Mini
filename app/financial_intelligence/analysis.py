
import pandas as pd

from app.financial_intelligence.calculations import (
    calculate_gross_margin,
    calculate_operating_margin,
    calculate_net_profit_margin,
)
from app.financial_intelligence.dataset import load_financial_dataset


def _number_or_none(value):
    if pd.isna(value):
        return None
    return float(value)


def get_company_financials(ticker: str, date=None) -> dict:
    """Return financial metrics for a company on a selected date."""
    df = load_financial_dataset()
    ticker = ticker.strip().upper()

    if "ticker" not in df.columns:
        raise ValueError("Dataset does not contain a recognized ticker column.")

    company_rows = df[df["ticker"] == ticker]

    if company_rows.empty:
        raise ValueError(f"Company ticker not found: {ticker}")

    if date is not None:
        requested_date = str(date)
        company_rows = company_rows[
            company_rows["period_end"].dt.strftime("%Y-%m-%d")
            == requested_date
        ]

        if company_rows.empty:
            raise ValueError(
                f"No financial record found for {ticker} on {requested_date}"
            )

    row = company_rows.sort_values("period_end").iloc[-1]

    revenue = _number_or_none(row["total_revenue"])
    gross_profit = _number_or_none(row.get("gross_profit"))
    operating_income = _number_or_none(row.get("operating_income"))
    net_income = _number_or_none(row.get("net_income"))

    return {
        "ticker": ticker,
        "company": str(row["company_name"]),
        "date": row["period_end"].strftime("%Y-%m-%d"),
        "total_revenue": revenue,
        "gross_profit": gross_profit,
        "operating_income": operating_income,
        "net_income": net_income,
        "gross_margin_pct": calculate_gross_margin(
            gross_profit, revenue
        ),
        "operating_margin_pct": calculate_operating_margin(
            operating_income, revenue
        ),
        "net_profit_margin_pct": calculate_net_profit_margin(
            net_income, revenue
        ),
    }


def compare_company_financials(
    ticker: str,
    start_date: str,
    end_date: str,
) -> dict:
    """Compare a company's financial metrics across two reporting dates."""
    df = load_financial_dataset()
    ticker = ticker.strip().upper()

    if "ticker" not in df.columns:
        raise ValueError("Dataset does not contain a recognized ticker column.")

    company_rows = df[df["ticker"] == ticker].copy()

    if company_rows.empty:
        raise ValueError(f"Company ticker not found: {ticker}")

    def get_row(date: str):
        matches = company_rows[
            company_rows["period_end"].dt.strftime("%Y-%m-%d") == date
        ]

        if matches.empty:
            raise ValueError(
                f"No financial record found for {ticker} on {date}"
            )

        return matches.iloc[0]

    start = get_row(start_date)
    end = get_row(end_date)

    metrics = {
        "total_revenue": "total_revenue",
        "gross_profit": "gross_profit",
        "operating_income": "operating_income",
        "net_income": "net_income",
    }

    comparison = {}

    for metric_name, column in metrics.items():
        start_value = _number_or_none(start.get(column))
        end_value = _number_or_none(end.get(column))

        if start_value is None or end_value is None:
            comparison[metric_name] = {
                "start_value": start_value,
                "end_value": end_value,
                "absolute_change": None,
                "percentage_change": None,
            }
            continue

        change = end_value - start_value

        comparison[metric_name] = {
            "start_value": start_value,
            "end_value": end_value,
            "absolute_change": round(change, 2),
            "percentage_change": (
                round((change / start_value) * 100, 2)
                if start_value != 0
                else None
            ),
        }

    return {
        "ticker": ticker,
        "company": str(end["company_name"]),
        "start_date": start_date,
        "end_date": end_date,
        "metrics": comparison,
    }
