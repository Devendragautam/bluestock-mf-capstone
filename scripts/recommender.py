"""
recommender.py

Day 6 -- Simple Fund Recommender (Bluestock MF Capstone)

Rule-based recommender that maps an investor's stated risk appetite
(Low / Moderate / High) to the matching SEBI risk categories and
returns the top-N funds by Sharpe ratio within that band.

Usage:
    python scripts/recommender.py
"""

from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine

DB_PATH = Path("data/db/bluestock_mf.db")

RISK_MAP = {
    "Low": ["Low"],
    "Moderate": ["Moderate", "Moderately High"],
    "High": ["High", "Very High"],
}


def recommend_funds(risk_appetite: str, db_path: Path = DB_PATH, top_n: int = 3) -> pd.DataFrame:
    """
    Recommend the top-N funds by Sharpe ratio matching an investor's
    risk appetite.

    Parameters
    ----------
    risk_appetite : str
        One of "Low", "Moderate", or "High".
    db_path : Path
        Path to the SQLite database.
    top_n : int
        Number of funds to return.

    Returns
    -------
    pd.DataFrame
        Top-N matching funds, sorted by Sharpe ratio descending.
    """
    if risk_appetite not in RISK_MAP:
        raise ValueError("risk_appetite must be 'Low', 'Moderate', or 'High'")

    engine = create_engine(f"sqlite:///{db_path}")
    query = """
        SELECT df.scheme_name, df.fund_house, df.risk_category, fp.sharpe_ratio
        FROM fact_performance fp
        JOIN dim_fund df ON fp.amfi_code = df.amfi_code
    """
    all_funds = pd.read_sql(query, engine)
    matching_funds = all_funds[all_funds["risk_category"].isin(RISK_MAP[risk_appetite])]
    return matching_funds.sort_values("sharpe_ratio", ascending=False).head(top_n)


def main() -> None:
    for appetite in ["Low", "Moderate", "High"]:
        print(f"\n=== Top 3 funds for {appetite} risk appetite ===")
        print(recommend_funds(appetite).to_string(index=False))


if __name__ == "__main__":
    main()
