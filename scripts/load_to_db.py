import pandas as pd
from sqlalchemy import create_engine, text

# Create the database file (this creates bluestock_mf.db if it doesn't exist)
engine = create_engine("sqlite:///data/db/bluestock_mf.db")

# First, run schema.sql to create the empty tables with proper structure
with open("sql/schema.sql", "r") as f:
    schema_sql = f.read()

with engine.connect() as conn:
    for statement in schema_sql.split(";"):
        statement = statement.strip()
        if statement:
            conn.execute(text(statement))
    conn.commit()

print("Schema created.")

# --- Load dim_fund ---
fund_master = pd.read_csv("data/raw/01_fund_master.csv")
fund_master = fund_master[[
    "amfi_code", "fund_house", "scheme_name", "category", "sub_category",
    "plan", "launch_date", "benchmark", "expense_ratio_pct", "exit_load_pct",
    "fund_manager", "risk_category", "sebi_category_code"
]]
fund_master.to_sql("dim_fund", engine, if_exists="append", index=False)
print("Loaded dim_fund:", len(fund_master), "rows")

# --- Load fact_nav ---
nav = pd.read_csv("data/processed/clean_nav.csv")
nav = nav.rename(columns={"date": "nav_date"})
nav["daily_return_pct"] = nav.groupby("amfi_code")["nav"].pct_change() * 100
nav.to_sql("fact_nav", engine, if_exists="append", index=False)
print("Loaded fact_nav:", len(nav), "rows")

# --- Load fact_transactions ---
tx = pd.read_csv("data/processed/clean_transactions.csv")
tx.to_sql("fact_transactions", engine, if_exists="append", index=False)
print("Loaded fact_transactions:", len(tx), "rows")

# --- Load fact_performance ---
perf = pd.read_csv("data/processed/clean_performance.csv")
perf = perf[[
    "amfi_code", "return_1yr_pct", "return_3yr_pct", "return_5yr_pct",
    "benchmark_3yr_pct", "alpha", "beta", "sharpe_ratio", "sortino_ratio",
    "std_dev_ann_pct", "max_drawdown_pct", "morningstar_rating"
]]
perf.to_sql("fact_performance", engine, if_exists="append", index=False)
print("Loaded fact_performance:", len(perf), "rows")

# --- Load fact_aum ---
aum = pd.read_csv("data/raw/03_aum_by_fund_house.csv")
aum = aum[["fund_house", "date", "aum_crore", "num_schemes"]]
aum.to_sql("fact_aum", engine, if_exists="append", index=False)
print("Loaded fact_aum:", len(aum), "rows")

# --- Load fact_sip_industry ---
sip = pd.read_csv("data/raw/04_monthly_sip_inflows.csv")
sip = sip[["month", "sip_inflow_crore", "active_sip_accounts_crore", "sip_aum_lakh_crore"]]
sip.to_sql("fact_sip_industry", engine, if_exists="append", index=False)
print("Loaded fact_sip_industry:", len(sip), "rows")

print("\nAll tables loaded successfully.")