"""
live_nav_fetch.py

Day 1 -- Live NAV Fetch (Bluestock MF Capstone)

Pulls live historical NAV data from the mfapi.in REST API (no
authentication required) for a fixed set of key schemes, and saves
each one as a raw CSV in data/raw/.

Usage:
    python scripts/live_nav_fetch.py
"""

from pathlib import Path

import pandas as pd
import requests

RAW_DIR = Path("data/raw")

# amfi_code -> short label used in the output filename
SCHEMES = {
    "125497": "HDFC_Top_100",
    "119551": "SBI_Bluechip",
    "120503": "ICICI_Bluechip",
    "118632": "Nippon_Large_Cap",
    "119092": "Axis_Bluechip",
    "120841": "Kotak_Bluechip",
}


def fetch_scheme_nav(amfi_code: str) -> pd.DataFrame:
    """Fetch full historical NAV for one scheme from the mfapi.in API."""
    url = f"https://api.mfapi.in/mf/{amfi_code}"
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    data = response.json()

    nav_df = pd.DataFrame(data["data"])
    nav_df["amfi_code"] = amfi_code
    nav_df["scheme_name"] = data["meta"]["scheme_name"]
    return nav_df


def fetch_all(schemes: dict = SCHEMES, raw_dir: Path = RAW_DIR) -> None:
    """Fetch and save NAV history for every scheme in `schemes`."""
    raw_dir.mkdir(parents=True, exist_ok=True)
    for code, name in schemes.items():
        nav_df = fetch_scheme_nav(code)
        out_path = raw_dir / f"live_nav_{code}_{name}.csv"
        nav_df.to_csv(out_path, index=False)
        print(f"Saved {name} ({code}): {len(nav_df)} rows -> {out_path}")


if __name__ == "__main__":
    fetch_all()
