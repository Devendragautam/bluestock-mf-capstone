"""
data_cleaning.py

Day 2 -- Data Cleaning (Bluestock MF Capstone)

Cleans the three core raw datasets (NAV history, investor transactions,
scheme performance) and writes them to data/processed/, then copies the
remaining seven raw datasets across unchanged (they passed validation
as-is during Day 1's data-quality checks) so that all ten source
datasets have a "clean" counterpart in data/processed/, as required by
the Day 2 deliverables list.

Usage:
    python scripts/data_cleaning.py
"""

import shutil
from pathlib import Path

import pandas as pd

RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")

PASS_THROUGH_FILES = [
    "01_fund_master.csv",
    "03_aum_by_fund_house.csv",
    "04_monthly_sip_inflows.csv",
    "05_category_inflows.csv",
    "06_industry_folio_count.csv",
    "09_portfolio_holdings.csv",
    "10_benchmark_indices.csv",
]


def clean_nav_history(raw_dir: Path = RAW_DIR, out_dir: Path = PROCESSED_DIR) -> pd.DataFrame:
    """Parse dates, forward-fill missing NAVs, drop duplicates, validate NAV > 0."""
    nav = pd.read_csv(raw_dir / "02_nav_history.csv")
    nav["date"] = pd.to_datetime(nav["date"])
    nav = nav.sort_values(["amfi_code", "date"])
    nav["nav"] = nav.groupby("amfi_code")["nav"].ffill()
    nav = nav.drop_duplicates()
    assert (nav["nav"] > 0).all(), "Found invalid NAV values!"

    out_dir.mkdir(parents=True, exist_ok=True)
    nav.to_csv(out_dir / "clean_nav.csv", index=False)
    print("Cleaned NAV rows:", len(nav))
    return nav


def clean_transactions(raw_dir: Path = RAW_DIR, out_dir: Path = PROCESSED_DIR) -> pd.DataFrame:
    """Standardise transaction type text, validate amounts, drop duplicates."""
    tx = pd.read_csv(raw_dir / "08_investor_transactions.csv")
    tx["transaction_date"] = pd.to_datetime(tx["transaction_date"])
    tx["transaction_type"] = tx["transaction_type"].str.strip().str.title()
    tx = tx[tx["amount_inr"] > 0]
    print("KYC status values found:", tx["kyc_status"].unique())
    tx = tx.drop_duplicates()

    out_dir.mkdir(parents=True, exist_ok=True)
    tx.to_csv(out_dir / "clean_transactions.csv", index=False)
    print("Cleaned transaction rows:", len(tx))
    return tx


def clean_performance(raw_dir: Path = RAW_DIR, out_dir: Path = PROCESSED_DIR) -> pd.DataFrame:
    """Coerce return/ratio columns to numeric and flag out-of-range values."""
    perf = pd.read_csv(raw_dir / "07_scheme_performance.csv")

    numeric_cols = [
        "return_1yr_pct", "return_3yr_pct", "return_5yr_pct",
        "sharpe_ratio", "sortino_ratio", "std_dev_ann_pct", "max_drawdown_pct",
    ]
    for col in numeric_cols:
        perf[col] = pd.to_numeric(perf[col], errors="coerce")

    print("Funds with negative Sharpe:", len(perf[perf["sharpe_ratio"] < 0]))
    bad_expense = perf[(perf["expense_ratio_pct"] < 0.1) | (perf["expense_ratio_pct"] > 2.5)]
    print("Funds with out-of-range expense ratio:", len(bad_expense))

    out_dir.mkdir(parents=True, exist_ok=True)
    perf.to_csv(out_dir / "clean_performance.csv", index=False)
    print("Cleaned performance rows:", len(perf))
    return perf


def copy_pass_through_files(
    filenames: list = PASS_THROUGH_FILES,
    raw_dir: Path = RAW_DIR,
    out_dir: Path = PROCESSED_DIR,
) -> None:
    """Copy the remaining raw datasets across as clean_<name>.csv."""
    out_dir.mkdir(parents=True, exist_ok=True)
    for fname in filenames:
        src = raw_dir / fname
        dst = out_dir / f"clean_{fname}"
        shutil.copy(src, dst)
        print(f"Copied {fname} -> {dst.name}")


def main() -> None:
    clean_nav_history()
    clean_transactions()
    clean_performance()
    copy_pass_through_files()


if __name__ == "__main__":
    main()
