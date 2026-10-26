
from datetime import date

from fastapi import FastAPI, HTTPException

from app.financial_intelligence.analysis import (
    compare_company_financials,
    get_company_financials,
)

app = FastAPI(
    title="Financial Intelligence API",
    description="Financial analysis and comparison using structured financial data.",
    version="0.1.0",
)


@app.get("/")
def home():
    return {
        "message": "Financial Intelligence API is running!",
        "status": "success",
    }


@app.get("/financial/{ticker}")
def company_financials(ticker: str, report_date: date | None = None):
    try:
        return get_company_financials(
            ticker,
            report_date.isoformat() if report_date else None,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/financial/{ticker}/compare")
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
