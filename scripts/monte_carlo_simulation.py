"""
monte_carlo_simulation.py

Bonus Challenge B3 -- Monte Carlo NAV Projection (Bluestock MF Capstone)

Projects 5-year NAV growth for the top 5 scorecard funds using a
Geometric Brownian Motion Monte Carlo simulation, calibrated to each
fund's own historical daily return mean and standard deviation.

For each fund, 2,000 independent 5-year price paths are simulated.
The median path and the 10th-90th percentile band (80% confidence
interval) are plotted and saved, alongside a summary CSV of the
projected 5-year return distribution per fund.

Methodology
-----------
Daily log returns are assumed i.i.d. Normal(mu, sigma), estimated from
each fund's full historical NAV series (data/processed/clean_nav.csv).
Each simulated path is:

    NAV_t = NAV_0 * exp(cumsum(mu - 0.5*sigma^2 + sigma * Z_t))

where Z_t ~ N(0, 1) i.i.d. across trading days, drawn independently
per path. This is a simplified projection tool, not a forecast --
it assumes returns are stationary and normally distributed, which is
a real limitation flagged in Final_Report.pdf.

Usage:
    python scripts/monte_carlo_simulation.py
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

PROCESSED_DIR = Path("data/processed")
CHARTS_DIR = Path("reports/charts")

TRADING_DAYS_PER_YEAR = 252
PROJECTION_YEARS = 5
N_SIMULATIONS = 2000
TOP_N_FUNDS = 5
RANDOM_SEED = 42


def load_top_funds(n: int = TOP_N_FUNDS, processed_dir: Path = PROCESSED_DIR) -> pd.DataFrame:
    """Return the top-N funds by composite scorecard score."""
    scorecard = pd.read_csv(processed_dir / "fund_scorecard.csv")
    return scorecard.sort_values("score", ascending=False).head(n)


def fund_return_stats(amfi_code: int, processed_dir: Path = PROCESSED_DIR) -> tuple:
    """Return (mu, sigma) -- the daily log-return mean and std for one fund."""
    nav = pd.read_csv(processed_dir / "clean_nav.csv")
    fund_nav = nav[nav["amfi_code"] == amfi_code].sort_values("date")
    log_returns = np.log(fund_nav["nav"] / fund_nav["nav"].shift(1)).dropna()
    return log_returns.mean(), log_returns.std(), fund_nav["nav"].iloc[-1]


def simulate_paths(
    nav_0: float, mu: float, sigma: float,
    years: int = PROJECTION_YEARS, n_sims: int = N_SIMULATIONS, seed: int = RANDOM_SEED,
) -> np.ndarray:
    """
    Simulate n_sims independent GBM price paths of length years*252 days.
    Returns an array of shape (n_sims, n_days + 1), including NAV_0.
    """
    rng = np.random.default_rng(seed)
    n_days = years * TRADING_DAYS_PER_YEAR
    shocks = rng.standard_normal((n_sims, n_days))
    daily_log_returns = (mu - 0.5 * sigma ** 2) + sigma * shocks
    log_paths = np.cumsum(daily_log_returns, axis=1)
    paths = nav_0 * np.exp(log_paths)
    paths = np.hstack([np.full((n_sims, 1), nav_0), paths])
    return paths


def plot_fund_projection(scheme_name: str, paths: np.ndarray, ax) -> dict:
    """Plot the median path + 10th-90th percentile band for one fund."""
    days = np.arange(paths.shape[1])
    years = days / TRADING_DAYS_PER_YEAR

    p10 = np.percentile(paths, 10, axis=0)
    p50 = np.percentile(paths, 50, axis=0)
    p90 = np.percentile(paths, 90, axis=0)

    ax.plot(years, p50, color="#1E2761", linewidth=1.8, label="Median projection")
    ax.fill_between(years, p10, p90, color="#1E2761", alpha=0.18, label="10th-90th percentile")
    ax.set_title(scheme_name, fontsize=10)
    ax.set_xlabel("Years")
    ax.set_ylabel("Projected NAV")
    ax.legend(fontsize=7, loc="upper left")

    nav_0 = paths[0, 0]
    final = paths[:, -1]
    return {
        "nav_start": nav_0,
        "median_5yr_nav": np.median(final),
        "p10_5yr_nav": np.percentile(final, 10),
        "p90_5yr_nav": np.percentile(final, 90),
        "median_5yr_return_pct": (np.median(final) / nav_0 - 1) * 100,
        "p10_5yr_return_pct": (np.percentile(final, 10) / nav_0 - 1) * 100,
        "p90_5yr_return_pct": (np.percentile(final, 90) / nav_0 - 1) * 100,
    }


def run_simulation(
    n_funds: int = TOP_N_FUNDS,
    processed_dir: Path = PROCESSED_DIR,
    charts_dir: Path = CHARTS_DIR,
) -> pd.DataFrame:
    """Run the full B3 Monte Carlo simulation and save chart + summary CSV."""
    top_funds = load_top_funds(n_funds, processed_dir)

    fig, axes = plt.subplots(1, n_funds, figsize=(4.2 * n_funds, 4.2), sharey=False)
    if n_funds == 1:
        axes = [axes]

    summary_rows = []
    for ax, (_, fund) in zip(axes, top_funds.iterrows()):
        amfi_code = fund["amfi_code"]
        scheme_name = fund["scheme_name"]
        mu, sigma, nav_0 = fund_return_stats(amfi_code, processed_dir)
        paths = simulate_paths(nav_0, mu, sigma)
        stats = plot_fund_projection(scheme_name, paths, ax)
        stats.update({"amfi_code": amfi_code, "scheme_name": scheme_name})
        summary_rows.append(stats)
        print(
            f"{scheme_name}: median 5yr return {stats['median_5yr_return_pct']:.1f}% "
            f"(80% CI: {stats['p10_5yr_return_pct']:.1f}% to {stats['p90_5yr_return_pct']:.1f}%)"
        )

    fig.suptitle(
        f"5-Year Monte Carlo NAV Projection — Top {n_funds} Scorecard Funds "
        f"({N_SIMULATIONS:,} simulations, 80% confidence band)",
        fontsize=12, y=1.03,
    )
    fig.tight_layout()

    charts_dir.mkdir(parents=True, exist_ok=True)
    out_path = charts_dir / "18_monte_carlo_projection.png"
    fig.savefig(out_path, dpi=200, bbox_inches="tight")
    print(f"\nSaved chart -> {out_path}")

    summary_df = pd.DataFrame(summary_rows)
    summary_path = processed_dir / "monte_carlo_summary.csv"
    summary_df.to_csv(summary_path, index=False)
    print(f"Saved summary -> {summary_path}")

    return summary_df


if __name__ == "__main__":
    run_simulation()
