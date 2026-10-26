
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DEFAULT_DATASET_PATH = (
    PROJECT_ROOT / "data" / "financial data sp500 companies.csv"
)

# Standard field name -> accepted input column names
COLUMN_ALIASES = {
    "company_name": ["company_name", "company", "firm", "company name"],
    "ticker": ["ticker", "symbol", "stock symbol"],
    "period_end": ["period_end", "date", "report date", "fiscal date"],
    "total_revenue": ["total_revenue", "total revenue", "revenue", "sales"],
    "gross_profit": ["gross_profit", "gross profit"],
    "operating_income": ["operating_income", "operating income", "ebit"],
    "net_income": ["net_income", "net income", "net profit"],
}


def _normalize_column_name(name: str) -> str:
    """Normalize column names for case-insensitive matching."""
    return " ".join(
        str(name).strip().lower().replace("_", " ").replace("-", " ").split()
    )


def load_financial_dataset(path=DEFAULT_DATASET_PATH) -> pd.DataFrame:
    """Load a CSV and normalize recognized columns into a common schema."""
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"Financial dataset not found: {path}")

    if path.suffix.lower() != ".csv":
        raise ValueError("This loader currently supports CSV files only.")

    df = pd.read_csv(path)

    # Remove common exported spreadsheet index columns.
    df = df.loc[
        :,
        ~df.columns.astype(str).str.match(r"^Unnamed:\s*\d+$", case=False),
    ].copy()

    # Match source columns to their canonical names.
    source_columns = {
        _normalize_column_name(column): column
        for column in df.columns
    }

    rename_map = {}

    for canonical_name, aliases in COLUMN_ALIASES.items():
        for alias in aliases:
            normalized_alias = _normalize_column_name(alias)

            if normalized_alias in source_columns:
                source_name = source_columns[normalized_alias]
                if source_name not in rename_map:
                    rename_map[source_name] = canonical_name
                break

    df = df.rename(columns=rename_map)

    required_columns = [
        "company_name",
        "period_end",
        "total_revenue",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            "CSV is missing required financial fields: "
            f"{missing_columns}. Available columns: {list(df.columns)}"
        )

    df["period_end"] = pd.to_datetime(
        df["period_end"], errors="coerce"
    )

    numeric_columns = [
        "total_revenue",
        "gross_profit",
        "operating_income",
        "net_income",
    ]

    for column in numeric_columns:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce")

    df["company_name"] = df["company_name"].astype("string").str.strip()

    if "ticker" in df.columns:
        df["ticker"] = (
            df["ticker"].astype("string").str.strip().str.upper()
        )

    # Do not silently discard invalid rows; keep them available
    # for a later validation and reporting stage.
    df = df.drop_duplicates().reset_index(drop=True)

    df.attrs["source_file"] = str(path.resolve())

    return df
