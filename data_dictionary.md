# Bluestock MF Capstone — Data Dictionary

## dim_fund
| Column | Type | Description |
|---|---|---|
| amfi_code | TEXT (PK) | Unique AMFI scheme code |
| fund_house | TEXT | AMC name |
| scheme_name | TEXT | Full scheme name |
| category | TEXT | Equity / Debt |
| sub_category | TEXT | Large Cap / Mid Cap / etc. |
| plan | TEXT | Regular or Direct |
| launch_date | DATE | Fund launch date |
| benchmark | TEXT | Official benchmark index |
| expense_ratio_pct | REAL | Annual expense ratio % |
| exit_load_pct | REAL | Exit load % |
| fund_manager | TEXT | Fund manager name |
| risk_category | TEXT | SEBI risk grade |
| sebi_category_code | TEXT | Internal SEBI code |

## fact_nav
| Column | Type | Description |
|---|---|---|
| amfi_code | TEXT (FK) | Links to dim_fund |
| nav_date | DATE | NAV date |
| nav | REAL | NAV value in Rs. |
| daily_return_pct | REAL | Day-over-day % change (computed) |

## fact_transactions
| Column | Type | Description |
|---|---|---|
| tx_id | INTEGER (PK) | Auto-generated transaction ID |
| investor_id | TEXT | Investor identifier |
| amfi_code | TEXT (FK) | Fund involved |
| transaction_date | DATE | Date of transaction |
| transaction_type | TEXT | SIP / Lumpsum / Redemption |
| amount_inr | INTEGER | Amount in Rupees |
| state, city, city_tier | TEXT | Investor location |
| age_group, gender, annual_income_lakh | — | Demographics |
| payment_mode, kyc_status | TEXT | Transaction metadata |

## fact_performance
| Column | Type | Description |
|---|---|---|
| amfi_code | TEXT (FK) | Fund reference |
| return_1yr_pct / 3yr / 5yr | REAL | Returns over periods |
| alpha, beta | REAL | Risk-adjusted performance vs benchmark |
| sharpe_ratio, sortino_ratio | REAL | Risk-adjusted return metrics |
| std_dev_ann_pct | REAL | Annualised volatility |
| max_drawdown_pct | REAL | Worst peak-to-trough decline |
| morningstar_rating | INTEGER | 1-5 star rating |

## fact_aum
| Column | Type | Description |
|---|---|---|
| fund_house | TEXT | AMC name |
| date | DATE | Quarter-end date |
| aum_crore | INTEGER | AUM in Rs. crore |
| num_schemes | INTEGER | Number of schemes offered |

## fact_sip_industry
| Column | Type | Description |
|---|---|---|
| month | TEXT | YYYY-MM |
| sip_inflow_crore | INTEGER | Total SIP inflow that month |
| active_sip_accounts_crore | REAL | Active SIP accounts (crore) |
| sip_aum_lakh_crore | REAL | Total SIP AUM (lakh crore) |

## Known Data Notes
- `fact_aum` contains multiple quarterly snapshots per fund house — filter by latest `date` for current AUM.
- Liquid fund category shows unusually high Sharpe ratios due to very low volatility — expected behavior, not a data error.
- ~[X]% of `fact_transactions.amfi_code` values reference funds outside the 40-scheme `dim_fund` master list (see Day 1 data quality check).