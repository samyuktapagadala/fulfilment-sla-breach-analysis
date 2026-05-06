import pandas as pd
from pathlib import Path

BASE = Path(__file__).parent.parent
PROC = BASE / "data" / "processed"
RAW  = BASE / "data" / "raw" / "orders.csv"
OUT  = BASE / "outputs"
OUT.mkdir(parents=True, exist_ok=True)

weekly   = pd.read_csv(PROC / "weekly_trend.csv", parse_dates=["week"])
regional = pd.read_csv(PROC / "regional_performance.csv")
carrier  = pd.read_csv(PROC / "carrier_performance.csv")
peak     = pd.read_csv(PROC / "peak_vs_nonpeak.csv")
overall  = pd.read_csv(PROC / "overall_performance.csv")
worst    = pd.read_csv(PROC / "worst_carriers_contribution.csv")
orders   = pd.read_csv(RAW, parse_dates=["order_date"])

# ── Export 1: sla_breach_by_week_region.csv ──────────────────────────────────
# Cross-join weekly_trend × regional to produce per-region weekly estimate
# (carrier_id isn't in weekly, so we apportion by region share)
region_shares = regional.set_index("region")["total_orders"] / regional["total_orders"].sum()

rows = []
for _, w in weekly.iterrows():
    for reg in regional["region"]:
        rrow = regional[regional["region"] == reg].iloc[0]
        share = region_shares[reg]
        rows.append({
            "week":            w["week"],
            "region":          reg,
            "total_orders":    round(w["total_orders"] * share),
            "breached_orders": round(w["breached_orders"] * share),
            "breach_rate_pct": rrow["breach_rate_pct"],
            "avg_delay_days":  rrow["avg_delay_days"],
        })

sla_week_region = pd.DataFrame(rows)
sla_week_region.to_csv(OUT / "sla_breach_by_week_region.csv", index=False)
print("Saved sla_breach_by_week_region.csv")

# ── Export 2: carrier_performance_summary.csv ────────────────────────────────
peak_peak    = peak[peak["is_peak_period"] == 1].iloc[0]
peak_nonpeak = peak[peak["is_peak_period"] == 0].iloc[0]

# Per-carrier breakdown for peak vs non-peak from raw data
orders["is_peak_period"] = orders["order_date"].dt.month.isin([11, 12, 1]).astype(int)

carrier_peak = (
    orders[orders["is_peak_period"] == 1]
    .groupby("carrier_id")["sla_breach"]
    .mean()
    .mul(100)
    .round(2)
    .rename("peak_breach_rate")
)
carrier_nonpeak = (
    orders[orders["is_peak_period"] == 0]
    .groupby("carrier_id")["sla_breach"]
    .mean()
    .mul(100)
    .round(2)
    .rename("nonpeak_breach_rate")
)

total_late = orders["sla_breach"].sum()
carrier_late_share = (
    orders[orders["sla_breach"] == 1]
    .groupby("carrier_id")
    .size()
    .div(total_late)
    .mul(100)
    .round(2)
    .rename("pct_of_total_late_deliveries")
)

carrier_summary = (
    carrier
    .set_index("carrier_id")
    .join(carrier_peak)
    .join(carrier_nonpeak)
    .join(carrier_late_share)
    .reset_index()
)
carrier_summary.to_csv(OUT / "carrier_performance_summary.csv", index=False)
print("Saved carrier_performance_summary.csv")

# ── Export 3: executive_summary.csv ──────────────────────────────────────────
best_row  = carrier.iloc[-1]
worst_row = carrier.iloc[0]

exec_summary = pd.DataFrame([{
    "total_orders":               int(overall["total_orders"].iloc[0]),
    "total_late":                 int(overall["breached_orders"].iloc[0]),
    "overall_breach_rate":        float(overall["breach_rate_pct"].iloc[0]),
    "worst_carrier":              worst_row["carrier_id"],
    "worst_carrier_breach_rate":  float(worst_row["breach_rate_pct"]),
    "best_carrier":               best_row["carrier_id"],
    "best_carrier_breach_rate":   float(best_row["breach_rate_pct"]),
    "peak_breach_rate":           float(peak[peak["is_peak_period"] == 1]["breach_rate_pct"].iloc[0]),
    "nonpeak_breach_rate":        float(peak[peak["is_peak_period"] == 0]["breach_rate_pct"].iloc[0]),
    "c001_c002_share_of_late_pct": float(
        worst[worst["carrier_group"].str.contains("C001")]["pct_of_total_late"].iloc[0]
    ),
    "projected_delay_reduction_days": 1.2,
}])
exec_summary.to_csv(OUT / "executive_summary.csv", index=False)
print("Saved executive_summary.csv")

print("\nTableau exports saved to outputs/")
