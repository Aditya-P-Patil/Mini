# Financial Intelligence Component — Integration Guide

## 1. Purpose

The Financial Intelligence component provides deterministic financial lookups, calculations, and comparisons for the AI Financial Research Assistant.

It is designed to complement the Hybrid RAG component:

- **RAG** retrieves relevant information from financial reports and documents.
- **Financial Intelligence** retrieves structured financial records and calculates metric changes.
- **The answer/orchestration layer** combines retrieved evidence and calculation results into a response for the user.

Financial calculations should use structured data rather than asking the language model to perform arithmetic from report text.

## 2. Current implementation

The component is located in `app/financial_intelligence/`.

Important modules:

- `analysis.py` — company financial lookups and comparisons.
- `calculations.py` — reusable financial calculation functions.
- `dataset.py` — loads and normalizes the financial CSV dataset.
- `schemas.py` — financial record data structure.
- `routes.py` — FastAPI router for integration with the shared backend.
- `api.py` — standalone FastAPI application for independent testing.
- `insights.py` — optional rule-based insight generation, if this module has been added to the current branch.

The current dataset is `data/financial data sp500 companies.csv`.

**Data-source note:** the existing implementation reads from a CSV file. A successful connection to Supabase does not mean this dataset has been migrated to PostgreSQL.

## 3. Environment setup

From the repository root, create and activate a Python virtual environment if one is not already active.

Windows PowerShell:

```powershell
python -m venv .venv-financial
.\.venv-financial\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

Install the dependencies declared by the repository, if a `requirements.txt` is available:

```powershell
python -m pip install -r requirements.txt
```

If the repository does not yet declare all component dependencies, verify and add the required packages to the shared dependency file rather than expecting every teammate to install packages manually. The component uses FastAPI, SQLAlchemy-related project dependencies where required, and the libraries needed to read and process its dataset.

The financial CSV must be present at the path expected by `dataset.py`.

## 4. Use the component directly from Python

When the RAG and Financial Intelligence components run inside the same Python project, the preferred integration is to import the analysis function directly.

Example:

```python
from app.financial_intelligence.analysis import (
    compare_company_financials,
)

result = compare_company_financials(
    "AAPL",
    "2020-09-26",
    "2021-06-26",
)
```

The function accepts a ticker and two reporting dates. It returns the comparison result produced by the current analysis implementation.

The RAG orchestration layer should validate the ticker and dates, handle missing data, and pass the returned result to the answer-generation layer.

To retrieve financial information for a company:

```python
from app.financial_intelligence.analysis import (
    get_company_financials,
)

result = get_company_financials("AAPL")
```

An optional reporting date can be supplied using the function's current signature.

Use the actual return structure from `analysis.py`; do not assume fields that are not present in the result.

## 5. FastAPI integration

The shared application should expose the financial router through `app/main.py`.

The router is defined in `app/financial_intelligence/routes.py`. The shared application should import and register it once:

```python
from app.financial_intelligence.routes import (
    router as financial_router,
)

app.include_router(financial_router)
```

Add this to the existing application without replacing or removing the document-ingestion or RAG routes.

The shared application should be the main entry point for team use:

```powershell
python -m uvicorn app.main:app --reload --port 8000
```

Open the API documentation at:

`http://127.0.0.1:8000/docs`

The standalone Financial Intelligence application is available for isolated testing:

```powershell
python -m uvicorn app.financial_intelligence.api:app --reload --port 8001
```

Open its documentation at:

`http://127.0.0.1:8001/docs`

The standalone app is a development/testing entry point. Teammates should not need to run it separately when the financial router is integrated into the shared backend.

## 6. Available HTTP endpoints

When the financial router is registered in the shared application:

### Retrieve financial data

```http
GET /financial/{ticker}
```

Example:

```http
GET /financial/AAPL
```

An optional report date can be supplied using the `date` query parameter.

### Compare financial data

```http
GET /financial/{ticker}/compare?start_date=2020-09-26&end_date=2021-06-26
```

Example request:

```http
GET /financial/AAPL/compare?start_date=2020-09-26&end_date=2021-06-26
```

The response contains the comparison generated by the current analysis function. Consult the live Swagger documentation for the exact response fields.

When using the standalone application, use port `8001`. When using the integrated application, use port `8000`, provided the shared server is running there.

## 7. Recommended RAG integration flow

For a user question that requires financial analysis:

1. Identify the company, ticker, and requested reporting periods.
2. Use RAG to retrieve relevant report passages for narrative questions and supporting evidence.
3. Call `compare_company_financials()` for structured metric comparisons.
4. Handle missing records and invalid date ranges explicitly.
5. Combine the calculated result with the retrieved report evidence.
6. Cite the document sources and identify the structured data source used for calculations.
7. Clearly distinguish calculated facts from explanations or inferences generated by the language model.

Example orchestration:

```python
from app.financial_intelligence.analysis import (
    compare_company_financials,
)

comparison = compare_company_financials(
    ticker,
    start_date,
    end_date,
)

# Pass `comparison` to the existing answer-generation layer.
# Combine it with retrieved report passages and their citations.
```

This is an integration pattern, not a complete RAG pipeline. The RAG layer should use its existing retrieval and answer-generation implementation.

## 8. Error handling

The HTTP router converts `ValueError` exceptions from the analysis layer into HTTP 404 responses. The comparison endpoint also returns HTTP 400 when the start date is not earlier than the end date.

Callers should handle unsuccessful requests and missing financial records without inventing values.

## 9. Testing

Run the project's tests from the repository root:

```powershell
python -m pytest -q
```

The Financial Intelligence component previously passed 12 tests in the development environment. Re-run tests after pulling or merging changes and report the current result rather than assuming the previous result still applies.

Test the integrated API using:

`http://127.0.0.1:8000/docs`

Test the standalone API using:

`http://127.0.0.1:8001/docs`

## 10. Shared database and configuration

The component currently reads its structured financial dataset from CSV. Supabase PostgreSQL is configured separately for the shared application.

Before moving financial records into PostgreSQL, coordinate with the team on the schema, data ownership, migrations, and source-of-truth policy. Do not assume the database contains financial records simply because the connection works.

Keep `.env` out of version control. Use `.env.example` with placeholder values only. Never commit database passwords or connection strings containing credentials.

## 11. Integration checklist

- [ ] Financial Intelligence files are committed to the shared repository.
- [ ] The required dataset is available to teammates.
- [ ] Dependencies are declared in the repository's shared dependency file.
- [ ] The financial router is registered in the shared FastAPI app.
- [ ] Existing RAG and document routes remain intact.
- [ ] Tests pass in a clean environment.
- [ ] The team has verified the API response structure.
- [ ] Database schema changes, if any, have been reviewed with the team.
- [ ] No secrets or local virtual-environment files are committed.
