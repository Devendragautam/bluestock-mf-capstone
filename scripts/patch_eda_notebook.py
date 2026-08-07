"""One-off: fill the gaps in notebooks/03_eda_analysis.ipynb.

- highlights the 2023 bull run / 2024 correction on the NAV trend chart
- adds the missing folio-count growth chart (Chart 7) with milestone markers
- drops the stray `pip install` cell and the duplicated geography cell
- adds supplementary charts so the notebook clears the 15-chart deliverable
- replaces the [Fill in] placeholders with findings computed from the data
"""
import json
from pathlib import Path

NB = Path(__file__).resolve().parents[1] / "notebooks" / "03_eda_analysis.ipynb"
nb = json.loads(NB.read_text(encoding="utf-8"))
cells = nb["cells"]


def code(src):
    return {"cell_type": "code", "execution_count": None, "metadata": {},
            "outputs": [], "source": src.strip("\n").splitlines(keepends=True)}


def md(src):
    return {"cell_type": "markdown", "metadata": {},
            "source": src.strip("\n").splitlines(keepends=True)}


def find(snippet):
    for i, c in enumerate(cells):
        if snippet in "".join(c["source"]):
            return i
    raise SystemExit("not found: " + snippet)


# --- 1. NAV trend: shade the 2023 bull run and the 2024 corrections ----------
cells[find("NAV Trend")] = code('''
fig = px.line(
    nav.sort_values(["amfi_code", "nav_date"]),
    x="nav_date",
    y="nav",
    color="amfi_code",
    title="NAV Trend — All 40 Schemes (2022–2026)"
)

# 2023 bull run
fig.add_vrect(x0="2023-03-01", x1="2023-12-31", fillcolor="green", opacity=0.10,
              line_width=0, annotation_text="2023 bull run", annotation_position="top left")

# 2024 corrections
for x0, x1, label in [("2024-01-15", "2024-03-15", "Q1-24 correction"),
                      ("2024-06-01", "2024-06-30", "Jun-24 correction"),
                      ("2024-10-01", "2024-11-30", "Oct–Nov-24 correction")]:
    fig.add_vrect(x0=x0, x1=x1, fillcolor="red", opacity=0.12, line_width=0,
                  annotation_text=label, annotation_position="top left")

fig.update_layout(showlegend=False, height=600,
                  xaxis_title="Date", yaxis_title="NAV (Rs.)")
fig.show()
''')

# --- 2. stray pip cell -> chart output dir -----------------------------------
cells[find("pip install -U kaleido")] = code('''
import os
os.makedirs("../reports/charts", exist_ok=True)
CHARTS = "../reports/charts"
''')

# --- 3. de-duplicate the geography cell -------------------------------------
geo = [i for i, c in enumerate(cells) if "T30 vs B30 City Tier Split" in "".join(c["source"])]
for i in reversed(geo[1:]):
    del cells[i]

# --- 4. clarify the heatmap window ------------------------------------------
i = find("Category-wise Net Inflow Heatmap")
cells[i]["source"] = [l.replace("FY 2024-25", "Apr 2024 – Mar 2025")
                      for l in cells[i]["source"]]

# --- 5. new charts, inserted before the findings markdown -------------------
new = [
    md("### Chart 7 — Industry folio count growth"),
    code('''
folios["month_dt"] = pd.to_datetime(folios["month"])
folios = folios.sort_values("month_dt")

fig, ax = plt.subplots(figsize=(13, 6))
ax.plot(folios["month_dt"], folios["total_folios_crore"], marker="o", lw=2,
        color="#1f77b4", label="Total folios")

milestones = [("2022-01", "13.26 Cr\\nJan 2022"),
              ("2023-03", "Crossed 15 Cr"),
              ("2024-03", "Crossed 17 Cr"),
              ("2025-12", "26.12 Cr\\nDec 2025")]
for m, label in milestones:
    row = folios[folios["month"] == m]
    if row.empty:
        continue
    x = row["month_dt"].iloc[0]
    y = row["total_folios_crore"].iloc[0]
    ax.scatter([x], [y], s=90, color="crimson", zorder=5)
    ax.annotate(f"{label}\\n({y:.2f} Cr)", (x, y), textcoords="offset points",
                xytext=(-10, 18), fontsize=9, ha="center", color="crimson")

ax.set_title("Industry Folio Count Growth (Jan 2022 – Dec 2025)")
ax.set_xlabel("Month")
ax.set_ylabel("Total folios (crore)")
ax.grid(alpha=0.3)
ax.legend()
plt.tight_layout()
plt.savefig(f"{CHARTS}/07_folio_count_growth.png", dpi=200)
plt.show()
'''),
    md("### Chart 11 — Folio mix by asset class"),
    code('''
fig, ax = plt.subplots(figsize=(13, 6))
ax.stackplot(folios["month_dt"],
             folios["equity_folios_crore"], folios["debt_folios_crore"],
             folios["hybrid_folios_crore"], folios["others_folios_crore"],
             labels=["Equity", "Debt", "Hybrid", "Others"],
             colors=["#4C72B0", "#DD8452", "#55A868", "#C44E52"], alpha=0.9)
ax.set_title("Folio Mix by Asset Class (2022–2025)")
ax.set_xlabel("Month")
ax.set_ylabel("Folios (crore)")
ax.legend(loc="upper left")
plt.tight_layout()
plt.savefig(f"{CHARTS}/11_folio_mix_by_asset_class.png", dpi=200)
plt.show()
'''),
    md("### Chart 12 — Normalised NAV growth (base 100) by category"),
    code('''
nav_cat = nav.merge(fund_master[["amfi_code", "category"]], on="amfi_code", how="left")
first = nav_cat.sort_values("nav_date").groupby("amfi_code")["nav"].transform("first")
nav_cat["indexed"] = nav_cat["nav"] / first * 100

cat_curve = nav_cat.groupby(["nav_date", "category"])["indexed"].mean().reset_index()

fig = px.line(cat_curve, x="nav_date", y="indexed", color="category",
              title="Normalised NAV Growth by Category (Base 100 = Jan 2022)")
fig.update_layout(height=500, xaxis_title="Date", yaxis_title="Indexed NAV")
fig.show()
fig.write_image(f"{CHARTS}/12_normalised_nav_by_category.png")
'''),
    md("### Chart 13 — Expense ratio: Regular vs Direct plans"),
    code('''
fig, ax = plt.subplots(figsize=(9, 6))
sns.boxplot(data=fund_master, x="plan", y="expense_ratio_pct", hue="plan",
            palette="Set2", legend=False, ax=ax)
sns.stripplot(data=fund_master, x="plan", y="expense_ratio_pct",
              color="black", alpha=0.5, size=4, ax=ax)
ax.set_title("Expense Ratio Distribution — Regular vs Direct Plans")
ax.set_ylabel("Expense ratio (%)")
plt.tight_layout()
plt.savefig(f"{CHARTS}/13_expense_ratio_by_plan.png", dpi=200)
plt.show()
'''),
    md("### Chart 14 — Monthly gross flows by transaction type"),
    code('''
tx = transactions.copy()
tx["transaction_date"] = pd.to_datetime(tx["transaction_date"])
tx["month"] = tx["transaction_date"].dt.to_period("M").dt.to_timestamp()

flows = (tx.groupby(["month", "transaction_type"])["amount_inr"].sum()
           .unstack(fill_value=0) / 1e7)  # to Rs. crore

fig, ax = plt.subplots(figsize=(13, 6))
flows.plot(kind="bar", stacked=True, ax=ax, colormap="viridis", width=0.85)
ax.set_title("Monthly Gross Flows by Transaction Type")
ax.set_xlabel("Month")
ax.set_ylabel("Amount (Rs. crore)")
ax.set_xticklabels([d.strftime("%b-%y") for d in flows.index], rotation=45, ha="right")
plt.tight_layout()
plt.savefig(f"{CHARTS}/14_monthly_flows_by_type.png", dpi=200)
plt.show()
'''),
    md("### Chart 15 — Net category inflow, ranked (Apr 2024 – Mar 2025)"),
    code('''
cat_total = (category_inflows.groupby("category")["net_inflow_crore"].sum()
             .sort_values())

fig, ax = plt.subplots(figsize=(10, 7))
sns.barplot(x=cat_total.values, y=cat_total.index, hue=cat_total.index,
            palette="crest", legend=False, ax=ax)
for i, v in enumerate(cat_total.values):
    ax.text(v, i, f" {v:,.0f}", va="center", fontsize=9)
ax.set_title("Total Net Inflow by Category (Apr 2024 – Mar 2025)")
ax.set_xlabel("Net inflow (Rs. crore)")
ax.set_ylabel("")
plt.tight_layout()
plt.savefig(f"{CHARTS}/15_category_net_inflow_ranked.png", dpi=200)
plt.show()
'''),
    md("### Chart 16 — SIP accounts and SIP AUM"),
    code('''
fig, ax1 = plt.subplots(figsize=(13, 6))
ax1.plot(sip["month"], sip["active_sip_accounts_crore"], color="#4C72B0",
         marker="o", ms=3, label="Active SIP accounts (Cr)")
ax1.set_ylabel("Active SIP accounts (crore)", color="#4C72B0")
ax1.set_xlabel("Month")

ax2 = ax1.twinx()
ax2.plot(sip["month"], sip["sip_aum_lakh_crore"], color="#C44E52",
         marker="s", ms=3, label="SIP AUM (Rs. lakh Cr)")
ax2.set_ylabel("SIP AUM (Rs. lakh crore)", color="#C44E52")

ax1.set_title("SIP Accounts vs SIP AUM (Jan 2022 – Dec 2025)")
ax1.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(f"{CHARTS}/16_sip_accounts_vs_aum.png", dpi=200)
plt.show()
'''),
    md("### Chart 17 — 30-day rolling volatility of the 10 selected funds"),
    code('''
roll_vol = returns_wide.rolling(30).std().dropna() * (252 ** 0.5) * 100

fig, ax = plt.subplots(figsize=(13, 6))
for c in roll_vol.columns:
    ax.plot(roll_vol.index, roll_vol[c], lw=1, alpha=0.8, label=c)
ax.set_title("30-Day Rolling Annualised Volatility — 10 Selected Funds")
ax.set_xlabel("Date")
ax.set_ylabel("Annualised volatility (%)")
ax.legend(fontsize=7, ncol=2)
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(f"{CHARTS}/17_rolling_volatility.png", dpi=200)
plt.show()
'''),
]

# category_inflows / returns_wide are defined earlier in the notebook, so append
# the new blocks immediately before the findings markdown.
findings_idx = find("Key EDA Findings")
cells[findings_idx:findings_idx] = new

# --- 6. real findings --------------------------------------------------------
findings_idx = find("Key EDA Findings")
cells[findings_idx] = md('''
## Key EDA Findings

1. **NAV levels are not comparable across funds** — launch NAVs differ by an order of
   magnitude, so absolute NAV lines say nothing about performance; the category curves must be
   rebased to 100 before they can be read. *(Chart 1, Chart 12)*
2. **SBI Mutual Fund is the clear AUM leader** — it grows from ₹6.05L Cr (Mar 2022) to
   **₹12.5L Cr (Dec 2025)**, roughly 16% ahead of ICICI Prudential (₹10.74L Cr) and 34% ahead of
   HDFC (₹9.30L Cr). *(Chart 2)*
3. **SIP inflows grew almost monotonically for 48 straight months**, from ~₹11.3k Cr in Jan 2022
   to an all-time high of **₹31,002 Cr in Dec 2025** — a ~2.7x rise with no sustained
   drawdown, i.e. SIP money behaved as a shock absorber rather than a pro-cyclical flow.
   *(Chart 3, Chart 16)*
4. **Liquid funds dominate the inflow heatmap and distort it** — ₹4.51L Cr of the FY25 net
   inflow is Liquid (peaking at ₹41,952 Cr in Aug 2024), ~4x the next category
   (Sectoral/Thematic, ₹1.04L Cr). These are treasury flows, not retail conviction, so the
   equity story only becomes visible once Liquid is set aside. *(Chart 4, Chart 15)*
5. **The investor base is young and concentrated** — 26–35 is the largest age group at
   **41.1%** of transactions and 36–45 adds 24.9%, so two thirds of activity comes from
   investors under 46. Median SIP size, though, is nearly flat across ages
   (₹5,020 for 18–25 vs ₹5,420 for 56+) — age drives *how many* SIPs, not how big.
   Gender split is **66.5% male / 33.5% female**. *(Chart 5)*
6. **SIP money is geographically flat, not metro-led** — Madhya Pradesh (₹20.7 Cr),
   Punjab (₹20.1 Cr) and Telangana (₹18.6 Cr) top the state table, and the top state leads
   the fifth by only ~13%. City tier is **66.3% T30 / 33.7% B30**, so B30 already supplies a
   third of transactions. *(Chart 6)*
7. **Folio count nearly doubled**, from **13.26 Cr (Jan 2022) to 26.12 Cr (Dec 2025)** — ~97%
   growth in four years. Equity folios drove it (9.28 Cr → 18.28 Cr) and their share of the
   total held steady at ~70%, so account growth was broad-based rather than a rotation into
   equity. *(Chart 7, Chart 11)*
8. **The daily-return correlation matrix is effectively empty** — pairwise correlations
   sit between –0.07 and +0.05 with a mean of –0.003. Real large-cap equity funds move
   together at 0.85–0.95, so this matrix cannot be used for diversification decisions
   as-is. *(Chart 8 — see finding 10)*
9. **Equity portfolios are financials-and-tech heavy** — Banking (19.2%), IT (13.4%) and
   Pharma (12.0%) account for **44.6%** of aggregate holding weight across all equity funds;
   the top six sectors reach 68.6%. Concentration this high means the "diversified equity"
   label understates single-sector exposure. *(Chart 9)*
10. **Anomaly — the NAV series is synthetic.** Regular and Direct plans of the *same*
    scheme (e.g. HDFC Top 100 Regular vs Direct) correlate at only **0.047** on daily returns;
    they hold an identical portfolio and should correlate at ~0.999, differing only by the
    expense-ratio drag (Direct averages 0.78% vs Regular 1.35%, Chart 13). Day-to-day NAV moves
    were therefore generated independently per scheme. Annual medians still look plausible
    (2022 +14.4%, 2023 +14.5%, 2024 +7.1%, 2025 +15.8%), so **level/trend analysis is usable but
    any daily-return statistic — correlation, beta, volatility — is not.**
    *(Charts 8, 13, 17)*
''')

NB.write_text(json.dumps(nb, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
print("patched:", len(cells), "cells")
