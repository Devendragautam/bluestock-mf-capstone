"""
data_ingestion.py

Day 1 -- Data Ingestion (Bluestock MF Capstone)

Loads every raw CSV in data/raw/, prints a shape/dtype/head summary for
each, then runs two data-quality checks:
    1. Lists the unique fund houses, categories, sub-categories and risk
       categories found in the fund master.
    2. Confirms every amfi_code in the fund master also appears in the
       NAV history, and flags any that don't.

Usage:
    python scripts/data_ingestion.py
"""

from pathlib import Path

import pandas as pd

RAW_DIR = Path("data/raw")


def profile_raw_csvs(raw_dir: Path = RAW_DIR) -> None:
    """Print shape, dtypes and head() for every CSV in raw_dir."""
    csv_files = sorted(raw_dir.glob("*.csv"))
    print(f"Found {len(csv_files)} CSV files\n")

    for file in csv_files:
        df = pd.read_csv(file)
        print("=" * 60)
        print(f"FILE: {file.name}")
        print(f"Shape: {df.shape}")
        print(f"Dtypes:\n{df.dtypes}")
        print(f"Head:\n{df.head()}")
        print()


def explore_fund_master(raw_dir: Path = RAW_DIR) -> pd.DataFrame:
    """Print the unique categorical values in the fund master and return it."""
    fund_master = pd.read_csv(raw_dir / "01_fund_master.csv")
    print("Unique fund houses:", fund_master["fund_house"].unique())
    print("Unique categories:", fund_master["category"].unique())
    print("Unique sub-categories:", fund_master["sub_category"].unique())
    print("Unique risk categories:", fund_master["risk_category"].unique())
    return fund_master


def validate_amfi_codes(fund_master: pd.DataFrame, raw_dir: Path = RAW_DIR) -> set:
    """
    Confirm every amfi_code in fund_master also appears in nav_history.

    Returns the set of codes present in fund_master but missing from
    nav_history (empty set if everything matches).
    """
    nav_history = pd.read_csv(raw_dir / "02_nav_history.csv")
    master_codes = set(fund_master["amfi_code"])
    nav_codes = set(nav_history["amfi_code"])
    missing_in_nav = master_codes - nav_codes

    print("\nData Quality Summary:")
    print(f"Fund master codes: {len(master_codes)}")
    print(f"NAV history unique codes: {len(nav_codes)}")
    print(f"Codes in master but missing from NAV history: {len(missing_in_nav)}")
    if missing_in_nav:
        print("Missing codes:", missing_in_nav)

    return missing_in_nav


def main() -> None:
    profile_raw_csvs()
    fund_master = explore_fund_master()
    validate_amfi_codes(fund_master)


if __name__ == "__main__":
    main()
