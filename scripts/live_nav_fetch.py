import requests
import pandas as pd

schemes = {
    "125497": "HDFC_Top_100",
    "119551": "SBI_Bluechip",
    "120503": "ICICI_Bluechip",
    "118632": "Nippon_Large_Cap",
    "119092": "Axis_Bluechip",
    "120841": "Kotak_Bluechip",
}

for code, name in schemes.items():
    url = f"https://api.mfapi.in/mf/{code}"
    response = requests.get(url)
    data = response.json()

    nav_df = pd.DataFrame(data["data"])
    nav_df["amfi_code"] = code
    nav_df["scheme_name"] = data["meta"]["scheme_name"]

    out_path = f"data/raw/live_nav_{code}_{name}.csv"
    nav_df.to_csv(out_path, index=False)
    print(f"Saved {name} ({code}): {len(nav_df)} rows -> {out_path}")