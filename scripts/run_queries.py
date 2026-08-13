"""
run_queries.py

Day 2 -- Run the 10 analytical SQL queries (Bluestock MF Capstone)

Reads sql/queries.sql (each query preceded by a "-- N. Label" comment),
runs every query against bluestock_mf.db, and prints the result as a
DataFrame.

Usage:
    python scripts/run_queries.py
"""

from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine

DB_PATH = Path("data/db/bluestock_mf.db")
QUERIES_PATH = Path("sql/queries.sql")


def run_all_queries(db_path: Path = DB_PATH, queries_path: Path = QUERIES_PATH) -> None:
    """Run every labelled query in queries_path and print its result."""
    engine = create_engine(f"sqlite:///{db_path}")
    content = queries_path.read_text()

    # Each query is preceded by a "-- Label" comment line; split on that.
    blocks = content.split("-- ")[1:]
    for block in blocks:
        label, _, sql = block.partition("\n")
        sql = sql.strip().rstrip(";")
        if not sql:
            continue
        print("=" * 60)
        print(label)
        df = pd.read_sql(sql, engine)
        print(df)
        print()


if __name__ == "__main__":
    run_all_queries()
