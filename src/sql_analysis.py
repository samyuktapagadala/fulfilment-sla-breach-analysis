import duckdb
import pandas as pd
from pathlib import Path

BASE = Path(__file__).parent.parent
RAW   = BASE / "data" / "raw"   / "orders.csv"
OUT   = BASE / "data" / "processed"
SQL   = BASE / "sql"  / "analysis_queries.sql"

OUT.mkdir(parents=True, exist_ok=True)

con = duckdb.connect()
orders_df = pd.read_csv(RAW, parse_dates=["order_date", "estimated_delivery", "actual_delivery"])
con.register("orders", orders_df)

# Query 1 – Overall SLA performance
q1 = """
SELECT
  COUNT(*) as total_orders,
  SUM(sla_breach) as breached_orders,
  ROUND(AVG(sla_breach)*100, 2) as breach_rate_pct,
  ROUND(AVG(delay_days), 2) as avg_delay_days
FROM orders
WHERE order_status = 'delivered'
"""
df1 = con.execute(q1).df()
df1.to_csv(OUT / "overall_performance.csv", index=False)
print("Query 1 done – overall_performance.csv")

# Query 2 – Breach rate by carrier
q2 = """
SELECT
  carrier_id,
  COUNT(*) as total_orders,
  SUM(sla_breach) as breached_orders,
  ROUND(AVG(sla_breach)*100, 2) as breach_rate_pct,
  ROUND(AVG(delay_days), 2) as avg_delay_days
FROM orders
WHERE order_status = 'delivered'
GROUP BY carrier_id
ORDER BY breach_rate_pct DESC
"""
df2 = con.execute(q2).df()
df2.to_csv(OUT / "carrier_performance.csv", index=False)
print("Query 2 done – carrier_performance.csv")

# Query 3 – Breach rate by region
q3 = """
SELECT
  region,
  COUNT(*) as total_orders,
  SUM(sla_breach) as breached_orders,
  ROUND(AVG(sla_breach)*100, 2) as breach_rate_pct,
  ROUND(AVG(delay_days), 2) as avg_delay_days
FROM orders
GROUP BY region
ORDER BY breach_rate_pct DESC
"""
df3 = con.execute(q3).df()
df3.to_csv(OUT / "regional_performance.csv", index=False)
print("Query 3 done – regional_performance.csv")

# Query 4 – Weekly breach trend
q4 = """
SELECT
  DATE_TRUNC('week', order_date::DATE) as week,
  COUNT(*) as total_orders,
  SUM(sla_breach) as breached_orders,
  ROUND(AVG(sla_breach)*100, 2) as breach_rate_pct
FROM orders
GROUP BY week
ORDER BY week
"""
df4 = con.execute(q4).df()
df4.to_csv(OUT / "weekly_trend.csv", index=False)
print("Query 4 done – weekly_trend.csv")

# Query 5 – Peak vs non-peak
q5 = """
SELECT
  is_peak_period,
  COUNT(*) as total_orders,
  ROUND(AVG(sla_breach)*100, 2) as breach_rate_pct,
  ROUND(AVG(delay_days), 2) as avg_delay_days
FROM orders
GROUP BY is_peak_period
"""
df5 = con.execute(q5).df()
df5.to_csv(OUT / "peak_vs_nonpeak.csv", index=False)
print("Query 5 done – peak_vs_nonpeak.csv")

# Query 6 – Worst carrier contribution
q6 = """
SELECT
  CASE WHEN carrier_id IN ('C001','C002')
    THEN 'C001 & C002 (Worst Carriers)'
    ELSE 'All Other Carriers'
  END as carrier_group,
  COUNT(*) as late_deliveries,
  ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as pct_of_total_late
FROM orders
WHERE sla_breach = 1
GROUP BY carrier_group
"""
df6 = con.execute(q6).df()
df6.to_csv(OUT / "worst_carriers_contribution.csv", index=False)

worst_pct = df6.loc[
    df6["carrier_group"].str.contains("C001"), "pct_of_total_late"
].values[0]
print(f"\nKEY FINDING: C001 and C002 account for {worst_pct}% of all late deliveries\n")
print("Query 6 done – worst_carriers_contribution.csv")

# Query 7 – Monthly trend
q7 = """
SELECT
  DATE_TRUNC('month', order_date::DATE) as month,
  COUNT(*) as total_orders,
  SUM(sla_breach) as breached_orders,
  ROUND(AVG(sla_breach)*100, 2) as breach_rate_pct,
  ROUND(AVG(delay_days), 2) as avg_delay_days,
  ROUND(SUM(order_value), 2) as total_revenue
FROM orders
GROUP BY month
ORDER BY month
"""
df7 = con.execute(q7).df()
df7.to_csv(OUT / "monthly_trend.csv", index=False)
print("Query 7 done – monthly_trend.csv")

print("\nAll 7 CSVs saved to data/processed/")
con.close()
