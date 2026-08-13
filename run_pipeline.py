"""
run_pipeline.py

Master ETL entry point (Bluestock MF Capstone)

Chains the core pipeline end to end:
    1. data_ingestion  -- profile raw CSVs, validate AMFI codes
    2. data_cleaning    -- clean NAV/transactions/performance, copy the rest
    3. load_to_db        -- (re)build the SQLite star schema and load it

Notebook-based steps (EDA, performance analytics, advanced analytics)
and the Power BI dashboard are run separately -- see README.md.

Usage:
    python run_pipeline.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "scripts"))

import data_ingestion   # noqa: E402
import data_cleaning    # noqa: E402
import load_to_db       # noqa: E402


def main() -> None:
    print("\n" + "=" * 60)
    print("STEP 1 / 3 -- Data ingestion")
    print("=" * 60)
    data_ingestion.main()

    print("\n" + "=" * 60)
    print("STEP 2 / 3 -- Data cleaning")
    print("=" * 60)
    data_cleaning.main()

    print("\n" + "=" * 60)
    print("STEP 3 / 3 -- Load into SQLite")
    print("=" * 60)
    load_to_db.main()

    print("\nPipeline complete. Database: data/db/bluestock_mf.db")


if __name__ == "__main__":
    main()
