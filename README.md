# Bluestock Mutual Fund Analytics Platform

An end-to-end data engineering, ETL pipeline, and interactive dashboard project for Bluestock Fintech's Mutual Fund Analytics capstone. Ingests publicly available AMFI India / mfapi.in mutual fund data, cleans and loads it into a 7-table SQLite star schema, computes performance and risk metrics, and presents everything through a 4-page interactive Power BI dashboard.

> Educational capstone project. Not financial advice. Fund identifiers, NAV anchors and AUM figures are sourced from real, public AMFI/mfapi.in data; investor transaction data is synthetically generated using realistic demographic and behavioural distributions.

## Contents

- [Project Overview](#project-overview)
- [Setup Instructions](#setup-instructions)
- [Running the ETL Pipeline](#running-the-etl-pipeline)
- [Running the Notebooks](#running-the-notebooks)
- [Opening the Dashboard](#opening-the-dashboard)
- [Repository Structure](#repository-structure)
- [Dataset Descriptions](#dataset-descriptions)
- [Deliverables](#deliverables)

## Project Overview

| | |
|---|---|
| **Domain** | Mutual Fund / Fintech |
| **Scope** | 40 real mutual fund schemes, 10 AMCs, ~46,000 NAV rows, ~32,800 investor transactions |
| **Pipeline** | Extract (AMFI CSVs + mfapi.in API) → Transform (pandas) → Load (SQLite star schema) → Analyse (Jupyter) → Visualise (Power BI) |
| **Report** | `reports/Final_Report.pdf` (also `.docx`) |
| **Slides** | `reports/Bluestock_MF_Presentation.pptx` (12 slides) |
| **Dashboard** | `dashboard/bluestock_mf_dashboard.pbix` (4 pages) |

## Setup Instructions

**Requirements:** Python 3.10+, Git, Power BI Desktop (Windows, for the dashboard).

```powershell
git clone https://github.com/Devendragautam/bluestock-mf-capstone.git
cd bluestock-mf-capstone

python -m venv venv
venv\Scripts\activate          # macOS/Linux: source venv/bin/activate

pip install -r requirements.txt
```

## Running the ETL Pipeline

The whole ingestion → cleaning → database-load sequence can be run in one command:

```powershell
python run_pipeline.py
```

This is safe to re-run — the database schema is dropped and recreated each time rather than failing on "table already exists."

Individual steps can also be run on their own if you want to inspect output between stages:

```powershell
python scripts/data_ingestion.py     # profile raw CSVs, validate AMFI codes
python scripts/live_nav_fetch.py     # optional: pull live NAV from mfapi.in
python scripts/data_cleaning.py      # clean NAV / transactions / performance
python scripts/load_to_db.py         # (re)build data/db/bluestock_mf.db
python scripts/run_queries.py        # run the 10 analytical SQL queries
python scripts/recommender.py        # sample fund recommendations by risk appetite
```

## Running the Notebooks

Open in VS Code or Jupyter Lab, selecting the `venv` kernel, and run top to bottom:

1. `notebooks/EDA_Analysis.ipynb` — 19 charts covering NAV trends, AUM growth, SIP flows, investor demographics, correlation structure and sector allocation.
2. `notebooks/Performance_Analytics.ipynb` — CAGR, Sharpe, Sortino, Alpha/Beta, Maximum Drawdown, and the composite fund scorecard.
3. `notebooks/advanced_analytics.ipynb` — VaR/CVaR, rolling 90-day Sharpe, investor cohort analysis, SIP continuity analysis, and sector concentration (HHI).

Each notebook writes its outputs (charts to `reports/charts/`, tables to `data/processed/`) so later steps and the dashboard can consume them.

## Opening the Dashboard

1. Install [Power BI Desktop](https://powerbi.microsoft.com/desktop) (free).
2. Open `dashboard/bluestock_mf_dashboard.pbix`.
3. If prompted to refresh data sources, point them at the CSVs in `data/processed/` (or the SQLite database at `data/db/bluestock_mf.db`).

The dashboard has 4 pages: **Industry Overview**, **Fund Performance**, **Investor Analytics**, and **SIP & Market Trends**, each with interactive slicers.

A static PDF export and PNG screenshots of every page are also available in `reports/` if Power BI Desktop isn't available.

## Repository Structure

```
bluestock-mf-capstone/
├── data/
│   ├── raw/              # Original provided + live-fetched CSVs
│   ├── processed/        # Cleaned CSVs + computed metric tables
│   └── db/                # bluestock_mf.db (SQLite, gitignored — rebuild via run_pipeline.py)
├── notebooks/
│   ├── EDA_Analysis.ipynb
│   ├── Performance_Analytics.ipynb
│   └── advanced_analytics.ipynb
├── scripts/
│   ├── data_ingestion.py
│   ├── live_nav_fetch.py
│   ├── data_cleaning.py
│   ├── load_to_db.py
│   ├── run_queries.py
│   └── recommender.py
├── sql/
│   ├── schema.sql        # Star schema DDL
│   └── queries.sql       # 10 analytical queries
├── dashboard/
│   └── bluestock_mf_dashboard.pbix
├── reports/
│   ├── Final_Report.pdf / .docx
│   ├── Bluestock_MF_Presentation.pptx
│   ├── Dashboard.pdf
│   ├── charts/                    # Exported PNGs from the notebooks
│   └── dashboard_screenshots/     # PNG per dashboard page
├── data_dictionary.md
├── run_pipeline.py
├── requirements.txt
└── README.md
```

## Dataset Descriptions

Ten datasets were provided as the primary input (see `data_dictionary.md` for full column-level detail):

| Dataset | Rows | Description |
|---|---|---|
| `01_fund_master.csv` | 40 | Master list of 40 real schemes — AMFI codes, fund house, category, expense ratio, risk grade |
| `02_nav_history.csv` | ~46,000 | Daily NAV for all 40 schemes, Jan 2022 – May 2026 |
| `03_aum_by_fund_house.csv` | ~90 | Quarterly AUM (Rs. crore), 10 fund houses, 2022–2025 |
| `04_monthly_sip_inflows.csv` | 48 | Monthly SIP inflow, active/new SIP accounts, SIP AUM |
| `05_category_inflows.csv` | ~144 | Net inflows by fund category, FY 2024–25 |
| `06_industry_folio_count.csv` | 21 | Total MF folios (crore), by Equity/Debt/Hybrid |
| `07_scheme_performance.csv` | 40 | 1/3/5yr returns, Sharpe, Sortino, Alpha, Beta, Max Drawdown |
| `08_investor_transactions.csv` | ~32,800 | Simulated SIP/Lumpsum/Redemption transactions, 5,000 investors |
| `09_portfolio_holdings.csv` | ~320 | Top equity holdings by stock, weight %, sector |
| `10_benchmark_indices.csv` | ~8,050 | Daily close values — Nifty 50/100/Midcap150, BSE SmallCap, CRISIL Liquid/Gilt |

## Deliverables

| Deliverable | Location |
|---|---|
| ETL pipeline | `run_pipeline.py`, `scripts/` |
| SQLite database (star schema) | `data/db/bluestock_mf.db` (rebuild via `run_pipeline.py`) |
| EDA notebook (19 charts) | `notebooks/EDA_Analysis.ipynb` |
| Performance metrics | `notebooks/Performance_Analytics.ipynb`, `data/processed/fund_scorecard.csv` |
| Advanced analytics + recommender | `notebooks/advanced_analytics.ipynb`, `scripts/recommender.py` |
| Interactive dashboard | `dashboard/bluestock_mf_dashboard.pbix` |
| Final report | `reports/Final_Report.pdf` |
| Presentation | `reports/Bluestock_MF_Presentation.pptx` |

## Known Limitations

See `reports/Final_Report.pdf`, Section 10, for full detail. In short:

- Analytics run on a 40-scheme sample, not the full ~1,908-scheme industry — dashboard KPI totals are proportionally smaller than real industry headline figures.
- Investor transaction data is synthetically generated (though built from realistic distributions).
- Dashboard Page 4 shows SIP inflow and Nifty 50 as two time-aligned charts rather than one true dual-axis visual — a cross-table relationship was built but did not filter correctly inside the combo visual.
- Drill-through was not implemented on the dashboard (time-boxed as optional).
