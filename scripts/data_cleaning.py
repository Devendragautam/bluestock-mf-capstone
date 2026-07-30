import pandas as pd

nav = pd.read_csv("data/raw/02_nav_history.csv")
nav["date"] = pd.to_datetime(nav["date"])
nav = nav.sort_values(["amfi_code", "date"])
nav["nav"] = nav.groupby("amfi_code")["nav"].ffill()
nav = nav.drop_duplicates()
assert (nav["nav"] > 0).all(), "Found invalid NAV values!"

nav.to_csv("data/processed/clean_nav.csv", index=False)
print("Cleaned NAV rows:", len(nav))

tx = pd.read_csv("data/raw/08_investor_transactions.csv")
tx["transaction_date"] = pd.to_datetime(tx["transaction_date"])
tx["transaction_type"] = tx["transaction_type"].str.strip().str.title()
tx = tx[tx["amount_inr"] > 0]
print("KYC status values found:", tx["kyc_status"].unique())
tx = tx.drop_duplicates()
tx.to_csv("data/processed/clean_transactions.csv", index=False)
print("Cleaned transaction rows:", len(tx))

perf = pd.read_csv("data/raw/07_scheme_performance.csv")

numeric_cols = ["return_1yr_pct", "return_3yr_pct", "return_5yr_pct",
                 "sharpe_ratio", "sortino_ratio", "std_dev_ann_pct", "max_drawdown_pct"]
for col in numeric_cols:
    perf[col] = pd.to_numeric(perf[col], errors="coerce")

print("Funds with negative Sharpe:", len(perf[perf["sharpe_ratio"] < 0]))
bad_expense = perf[(perf["expense_ratio_pct"] < 0.1) | (perf["expense_ratio_pct"] > 2.5)]
print("Funds with out-of-range expense ratio:", len(bad_expense))

perf.to_csv("data/processed/clean_performance.csv", index=False)
print("Cleaned performance rows:", len(perf))


import shutil
from pathlib import Path

remaining_files = [
    "01_fund_master.csv", "03_aum_by_fund_house.csv", "04_monthly_sip_inflows.csv",
    "05_category_inflows.csv", "06_industry_folio_count.csv",
    "09_portfolio_holdings.csv", "10_benchmark_indices.csv"
]

for fname in remaining_files:
    src = Path("data/raw") / fname
    dst = Path("data/processed") / f"clean_{fname}"
    shutil.copy(src, dst)
    print(f"Copied {fname} -> {dst.name}")