import pytest

from app.financial_intelligence.calculations import (
    calculate_gross_margin,
    calculate_operating_margin,
    calculate_net_profit_margin,
)


def test_gross_margin():
    assert calculate_gross_margin(60, 100) == 60.0


def test_operating_margin():
    assert calculate_operating_margin(20, 100) == 20.0


def test_net_profit_margin():
    assert calculate_net_profit_margin(15, 100) == 15.0


def test_negative_profit():
    assert calculate_net_profit_margin(-5, 100) == -5.0


def test_zero_revenue():
    assert calculate_gross_margin(60, 0) is None


def test_missing_profit():
    assert calculate_gross_margin(None, 100) is None


def test_negative_revenue():
    assert calculate_gross_margin(60, -100) is None
