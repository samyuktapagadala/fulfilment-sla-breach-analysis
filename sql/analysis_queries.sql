-- Query 1: Overall SLA performance
SELECT
  COUNT(*) as total_orders,
  SUM(sla_breach) as breached_orders,
  ROUND(AVG(sla_breach)*100, 2) as breach_rate_pct,
  ROUND(AVG(delay_days), 2) as avg_delay_days
FROM orders
WHERE order_status = 'delivered';

-- Query 2: Breach rate by carrier
SELECT
  carrier_id,
  COUNT(*) as total_orders,
  SUM(sla_breach) as breached_orders,
  ROUND(AVG(sla_breach)*100, 2) as breach_rate_pct,
  ROUND(AVG(delay_days), 2) as avg_delay_days
FROM orders
WHERE order_status = 'delivered'
GROUP BY carrier_id
ORDER BY breach_rate_pct DESC;

-- Query 3: Breach rate by region
SELECT
  region,
  COUNT(*) as total_orders,
  SUM(sla_breach) as breached_orders,
  ROUND(AVG(sla_breach)*100, 2) as breach_rate_pct,
  ROUND(AVG(delay_days), 2) as avg_delay_days
FROM orders
GROUP BY region
ORDER BY breach_rate_pct DESC;

-- Query 4: Weekly breach trend
SELECT
  DATE_TRUNC('week', order_date::DATE) as week,
  COUNT(*) as total_orders,
  SUM(sla_breach) as breached_orders,
  ROUND(AVG(sla_breach)*100, 2) as breach_rate_pct
FROM orders
GROUP BY week
ORDER BY week;

-- Query 5: Peak vs non-peak performance
SELECT
  is_peak_period,
  COUNT(*) as total_orders,
  ROUND(AVG(sla_breach)*100, 2) as breach_rate_pct,
  ROUND(AVG(delay_days), 2) as avg_delay_days
FROM orders
GROUP BY is_peak_period;

-- Query 6: Top 2 worst carriers contribution to total late deliveries
SELECT
  CASE WHEN carrier_id IN ('C001','C002')
    THEN 'C001 & C002 (Worst Carriers)'
    ELSE 'All Other Carriers'
  END as carrier_group,
  COUNT(*) as late_deliveries,
  ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as pct_of_total_late
FROM orders
WHERE sla_breach = 1
GROUP BY carrier_group;

-- Query 7: Monthly order volume and breach trend
SELECT
  DATE_TRUNC('month', order_date::DATE) as month,
  COUNT(*) as total_orders,
  SUM(sla_breach) as breached_orders,
  ROUND(AVG(sla_breach)*100, 2) as breach_rate_pct,
  ROUND(AVG(delay_days), 2) as avg_delay_days,
  ROUND(SUM(order_value), 2) as total_revenue
FROM orders
GROUP BY month
ORDER BY month;
