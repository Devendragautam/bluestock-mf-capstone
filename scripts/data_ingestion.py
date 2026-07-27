import pandas as pd
from pathlib import Path

raw_folder = Path("data/raw")
csv_files = sorted(raw_folder.glob("*.csv"))

print(f"Found {len(csv_files)} CSV files\n")

for file in csv_files:
    df = pd.read_csv(file)
    print("=" * 60)
    print(f"FILE: {file.name}")
    print(f"Shape: {df.shape}")
    print(f"Dtypes:\n{df.dtypes}")
    print(f"Head:\n{df.head()}")
    print()

# --- Task 6: Explore fund master ---
fund_master = pd.read_csv("data/raw/01_fund_master.csv")
print("Unique fund houses:", fund_master["fund_house"].unique())
print("Unique categories:", fund_master["category"].unique())
print("Unique sub-categories:", fund_master["sub_category"].unique())
print("Unique risk categories:", fund_master["risk_category"].unique())

# --- Task 7: Validate AMFI codes ---
nav_history = pd.read_csv("data/raw/02_nav_history.csv")
master_codes = set(fund_master["amfi_code"])
nav_codes = set(nav_history["amfi_code"])
missing_in_nav = master_codes - nav_codes

print(f"\nData Quality Summary:")
print(f"Fund master codes: {len(master_codes)}")
print(f"NAV history unique codes: {len(nav_codes)}")
print(f"Codes in master but missing from NAV history: {len(missing_in_nav)}")
if missing_in_nav:
    print("Missing codes:", missing_in_nav)
    
