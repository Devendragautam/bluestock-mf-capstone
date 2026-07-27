-- 1. Top 5 funds by AUM
SELECT fund_house, aum_crore FROM fact_aum
ORDER BY aum_crore DESC LIMIT 5;

-- 2. Average NAV per month for a given fund (example: 119551)
SELECT strftime('%Y-%m', nav_date) AS month, AVG(nav) AS avg_nav
FROM fact_nav
WHERE amfi_code = '119551'
GROUP BY month
ORDER BY month;

-- 3. SIP inflow month over month (basic trend, no YoY calc needed in SQL)
SELECT month, sip_inflow_crore FROM fact_sip_industry
ORDER BY month;

-- 4. Transactions by state
SELECT state, COUNT(*) AS num_transactions, SUM(amount_inr) AS total_amount
FROM fact_transactions
GROUP BY state
ORDER BY total_amount DESC;

-- 5. Funds with expense ratio below 1%
SELECT scheme_name, fund_house, expense_ratio_pct
FROM dim_fund
WHERE expense_ratio_pct < 1.0
ORDER BY expense_ratio_pct;

-- 6. Top 5 funds by Sharpe ratio
SELECT df.scheme_name, fp.sharpe_ratio
FROM fact_performance fp
JOIN dim_fund df ON fp.amfi_code = df.amfi_code
ORDER BY fp.sharpe_ratio DESC LIMIT 5;

-- 7. Transaction type breakdown (SIP vs Lumpsum vs Redemption)
SELECT transaction_type, COUNT(*) AS count, SUM(amount_inr) AS total
FROM fact_transactions
GROUP BY transaction_type;

-- 8. Funds by risk category count
SELECT risk_category, COUNT(*) AS num_funds
FROM dim_fund
GROUP BY risk_category;

-- 9. Average SIP amount by age group
SELECT age_group, AVG(amount_inr) AS avg_amount
FROM fact_transactions
WHERE transaction_type = 'Sip'
GROUP BY age_group;

-- 10. Highest single-day NAV drop per fund (simple volatility proxy)
SELECT amfi_code, MIN(daily_return_pct) AS worst_daily_return
FROM fact_nav
GROUP BY amfi_code
ORDER BY worst_daily_return ASC
LIMIT 5;