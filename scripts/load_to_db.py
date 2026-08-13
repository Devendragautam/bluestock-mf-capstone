"""
load_to_db.py

Day 2 -- Load cleaned data into SQLite (Bluestock MF Capstone)

Builds the bluestock_mf.db star schema from sql/schema.sql and loads
all seven tables (dim_date, dim_fund, fact_nav, fact_transactions,
fact_performance, fact_aum, fact_sip_industry) from the cleaned CSVs
in data/processed/ and the raw CSVs in data/raw/.

Safe to re-run: existing tables are dropped and recreated each time,
so this script is idempotent rather than failing with
"table already exists" on a second run.

Usage:
    python scripts/load_to_db.py
"""

from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text

DB_PATH = Path("data/db/bluestock_mf.db")
SCHEMA_PATH = Path("sql/schema.sql")
RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")

TABLE_NAMES = [
    "dim_date", "dim_fund", "fact_nav", "fact_transactions",
    "fact_performance", "fact_aum", "fact_sip_industry",
]


def get_engine(db_path: Path = DB_PATH):
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return create_engine(f"sqlite:///{db_path}")


def rebuild_schema(engine, schema_path: Path = SCHEMA_PATH) -> None:
    """Drop any existing tables, then recreate them from schema.sql."""
    with engine.connect() as conn:
        for table in TABLE_NAMES:
            conn.execute(text(f"DROP TABLE IF EXISTS {table}"))
        conn.commit()

    schema_sql = schema_path.read_text()
    with engine.connect() as conn:
        for statement in schema_sql.split(";"):
            statement = statement.strip()
            if statement:
                conn.execute(text(statement))
        conn.commit()
    print("Schema created.")


def load_dim_date(engine, start="2022-01-01", end="2026-05-31") -> None:
    """Build and load a calendar dimension covering the NAV date range."""
    all_dates = pd.date_range(start=start, end=end, freq="D")
    dim_date = pd.DataFrame({"date": all_dates})
    dim_date["date_id"] = dim_date["date"].dt.strftime("%Y%m%d")
    dim_date["year"] = dim_date["date"].dt.year
    dim_date["month"] = dim_date["date"].dt.month
    dim_date["quarter"] = dim_date["date"].dt.quarter
    dim_date["is_weekday"] = dim_date["date"].dt.dayofweek < 5
    dim_date.to_sql("dim_date", engine, if_exists="append", index=False)
    print("Loaded dim_date:", len(dim_date), "rows")


def load_dim_fund(engine, raw_dir: Path = RAW_DIR) -> None:
    fund_master = pd.read_csv(raw_dir / "01_fund_master.csv")
    fund_master = fund_master[[
        "amfi_code", "fund_house", "scheme_name", "category", "sub_category",
        "plan", "launch_date", "benchmark", "expense_ratio_pct", "exit_load_pct",
        "fund_manager", "risk_category", "sebi_category_code",
    ]]
    fund_master.to_sql("dim_fund", engine, if_exists="append", index=False)
    print("Loaded dim_fund:", len(fund_master), "rows")


def load_fact_nav(engine, processed_dir: Path = PROCESSED_DIR) -> None:
    nav = pd.read_csv(processed_dir / "clean_nav.csv")
    nav = nav.rename(columns={"date": "nav_date"})
    nav["daily_return_pct"] = nav.groupby("amfi_code")["nav"].pct_change() * 100
    nav.to_sql("fact_nav", engine, if_exists="append", index=False)
    print("Loaded fact_nav:", len(nav), "rows")


def load_fact_transactions(engine, processed_dir: Path = PROCESSED_DIR) -> None:
    tx = pd.read_csv(processed_dir / "clean_transactions.csv")
    tx.to_sql("fact_transactions", engine, if_exists="append", index=False)
    print("Loaded fact_transactions:", len(tx), "rows")


def load_fact_performance(engine, processed_dir: Path = PROCESSED_DIR) -> None:
    perf = pd.read_csv(processed_dir / "clean_performance.csv")
    perf = perf[[
        "amfi_code", "return_1yr_pct", "return_3yr_pct", "return_5yr_pct",
        "benchmark_3yr_pct", "alpha", "beta", "sharpe_ratio", "sortino_ratio",
        "std_dev_ann_pct", "max_drawdown_pct", "morningstar_rating",
    ]]
    perf.to_sql("fact_performance", engine, if_exists="append", index=False)
    print("Loaded fact_performance:", len(perf), "rows")


def load_fact_aum(engine, raw_dir: Path = RAW_DIR) -> None:
    aum = pd.read_csv(raw_dir / "03_aum_by_fund_house.csv")
    aum = aum[["fund_house", "date", "aum_crore", "num_schemes"]]
    aum.to_sql("fact_aum", engine, if_exists="append", index=False)
    print("Loaded fact_aum:", len(aum), "rows")


def load_fact_sip_industry(engine, raw_dir: Path = RAW_DIR) -> None:
    sip = pd.read_csv(raw_dir / "04_monthly_sip_inflows.csv")
    sip = sip[["month", "sip_inflow_crore", "active_sip_accounts_crore", "sip_aum_lakh_crore"]]
    sip.to_sql("fact_sip_industry", engine, if_exists="append", index=False)
    print("Loaded fact_sip_industry:", len(sip), "rows")


def main() -> None:
    engine = get_engine()
    rebuild_schema(engine)
    load_dim_date(engine)
    load_dim_fund(engine)
    load_fact_nav(engine)
    load_fact_transactions(engine)
    load_fact_performance(engine)
    load_fact_aum(engine)
    load_fact_sip_industry(engine)
    print("\nAll tables loaded successfully.")


if __name__ == "__main__":
    main()
