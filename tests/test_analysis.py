
import pytest

from app.financial_intelligence.analysis import (
    get_company_financials,
    compare_company_financials,
)


def test_company_lookup():
    result = get_company_financials("AAPL")

    assert result["ticker"] == "AAPL"
    assert result["company"]
    assert result["date"] == "2021-06-26"
    assert result["total_revenue"] > 0


def test_company_lookup_is_case_insensitive():
    result = get_company_financials("aapl")

    assert result["ticker"] == "AAPL"


def test_unknown_company_raises_error():
    with pytest.raises(ValueError, match="Company ticker not found"):
        get_company_financials("INVALID_TICKER")


def test_financial_comparison():
    result = compare_company_financials(
        "AAPL",
        "2020-09-26",
        "2021-06-26",
    )

    assert result["ticker"] == "AAPL"
    assert result["start_date"] == "2020-09-26"
    assert result["end_date"] == "2021-06-26"

    revenue = result["metrics"]["total_revenue"]

    assert revenue["start_value"] == 64698000000.0
    assert revenue["end_value"] == 81434000000.0
    assert revenue["absolute_change"] == 16736000000.0
    assert revenue["percentage_change"] == 25.87


def test_missing_reporting_date_raises_error():
    with pytest.raises(ValueError, match="No financial record found"):
        compare_company_financials(
            "AAPL",
            "2019-01-01",
            "2021-06-26",
        )
