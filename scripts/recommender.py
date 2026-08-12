import pandas as pd
from sqlalchemy import create_engine

def recommend_funds(risk_appetite, db_path="data/db/bluestock_mf.db", top_n=3):
    """
    Recommend top funds by Sharpe ratio matching the investor's risk appetite.
    risk_appetite: 'Low', 'Moderate', or 'High'
    """
    engine = create_engine(f"sqlite:///{db_path}")

    risk_map = {
        "Low": ["Low"],
        "Moderate": ["Moderate", "Moderately High"],
        "High": ["High", "Very High"]
    }

    if risk_appetite not in risk_map:
        raise ValueError("risk_appetite must be 'Low', 'Moderate', or 'High'")

    query = """
    SELECT df.scheme_name, df.fund_house, df.risk_category, fp.sharpe_ratio
    FROM fact_performance fp
    JOIN dim_fund df ON fp.amfi_code = df.amfi_code
    """
    all_funds = pd.read_sql(query, engine)
    matching_funds = all_funds[all_funds["risk_category"].isin(risk_map[risk_appetite])]
    top_funds = matching_funds.sort_values("sharpe_ratio", ascending=False).head(top_n)
    return top_funds

if __name__ == "__main__":
    for appetite in ["Low", "Moderate", "High"]:
        print(f"\n=== Top 3 funds for {appetite} risk appetite ===")
        print(recommend_funds(appetite).to_string(index=False))
        


