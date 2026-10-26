
from datetime import date

from fastapi import APIRouter, HTTPException, Query

from app.financial_intelligence.analysis import (
    compare_company_financials,
    get_company_financials,
)

router = APIRouter(prefix="/financial", tags=["Financial Intelligence"])


@router.get("/{ticker}")
def company_financials(
    ticker: str,
    report_date: date | None = Query(default=None, alias="date"),
):
    try:
        return get_company_financials(
            ticker,
            report_date.isoformat() if report_date else None,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/{ticker}/compare")
def compare_financials(
    ticker: str,
    start_date: date,
    end_date: date,
):
    if start_date >= end_date:
        raise HTTPException(
            status_code=400,
            detail="start_date must be earlier than end_date.",
        )

    try:
        return compare_company_financials(
            ticker,
            start_date.isoformat(),
            end_date.isoformat(),
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
