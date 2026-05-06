import pandas as pd
import numpy as np
from pathlib import Path

rng = np.random.default_rng(42)

N = 100_000

output_path = Path(__file__).parent.parent / "data" / "raw" / "orders.csv"
output_path.parent.mkdir(parents=True, exist_ok=True)

order_ids = [f"ORD{str(i).zfill(6)}" for i in range(1, N + 1)]

customer_ids = [f"CUST{str(rng.integers(1, 10001)).zfill(5)}" for _ in range(N)]
seller_ids   = [f"SELL{str(rng.integers(1, 501)).zfill(3)}"   for _ in range(N)]
carrier_ids  = [f"C{str(rng.integers(1, 11)).zfill(3)}"       for _ in range(N)]

start = pd.Timestamp("2022-01-01")
end   = pd.Timestamp("2023-06-30")
span  = (end - start).days
order_dates = pd.to_datetime(
    [start + pd.Timedelta(days=int(d)) for d in rng.integers(0, span + 1, N)]
)

estimated_delivery = order_dates + pd.to_timedelta(
    rng.integers(3, 8, N), unit="D"
)

is_peak = np.isin(order_dates.month, [11, 12, 1]).astype(int)

carrier_arr = np.array(carrier_ids)
delay_days_arr = np.zeros(N, dtype=int)

for i in range(N):
    cid = carrier_arr[i]
    peak = bool(is_peak[i])
    if cid in ("C001", "C002"):
        breach_prob = 0.65 if peak else 0.55
    elif cid in ("C003", "C004"):
        breach_prob = 0.22 if peak else 0.18
    else:
        breach_prob = 0.06 if peak else 0.04

    if rng.random() < breach_prob:
        delay_days_arr[i] = int(rng.integers(1, 15))

actual_delivery = estimated_delivery + pd.to_timedelta(delay_days_arr, unit="D")

regions      = ["Leinster", "Munster", "Connacht", "Ulster"]
region_probs = [0.45, 0.30, 0.15, 0.10]
region_arr   = rng.choice(regions, size=N, p=region_probs)

statuses      = ["delivered", "cancelled", "returned"]
status_probs  = [0.88, 0.07, 0.05]
status_arr    = rng.choice(statuses, size=N, p=status_probs)

item_count_arr  = rng.integers(1, 11, N)
order_value_arr = np.round(rng.uniform(10, 500, N), 2)

sla_breach_arr  = (delay_days_arr > 0).astype(int)
late_delivery_arr = sla_breach_arr.copy()

df = pd.DataFrame({
    "order_id":          order_ids,
    "customer_id":       customer_ids,
    "seller_id":         seller_ids,
    "carrier_id":        carrier_ids,
    "order_date":        order_dates.strftime("%Y-%m-%d"),
    "estimated_delivery": estimated_delivery.strftime("%Y-%m-%d"),
    "actual_delivery":   actual_delivery.strftime("%Y-%m-%d"),
    "region":            region_arr,
    "order_status":      status_arr,
    "item_count":        item_count_arr,
    "order_value":       order_value_arr,
    "is_peak_period":    is_peak,
    "sla_breach":        sla_breach_arr,
    "delay_days":        delay_days_arr,
    "late_delivery":     late_delivery_arr,
})

df.to_csv(output_path, index=False)

total = len(df)
print(f"orders.csv saved with {total:,} rows to {output_path}")

late_df = df[df["sla_breach"] == 1]
c001c002 = late_df[late_df["carrier_id"].isin(["C001", "C002"])]
pct = round(len(c001c002) / len(late_df) * 100, 1)
print(f"C001+C002 share of late deliveries: {pct}%")
print(f"Overall breach rate: {round(df['sla_breach'].mean()*100, 1)}%")
