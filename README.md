# Fulfilment Delay & SLA Breach Analysis

## Business Problem
Operations teams managing large fulfilment networks struggle to identify which carriers and routes are driving SLA breaches — especially during peak periods. Manual Excel reports lack the granularity to act quickly. This project analyses 100K+ orders across 18 months to pinpoint breach drivers and deliver actionable recommendations.

## Dataset
Synthetic dataset of 100,000 orders modelled on e-commerce fulfilment data (based on Kaggle Brazilian E-Commerce dataset structure).
18 months of data: January 2022 – June 2023.

## Approach
1. Generated realistic synthetic order data with carrier-level performance variation
2. Ran all analysis in SQL (DuckDB) for scalability and reproducibility
3. Visualised findings across 7 charts
4. Exported Tableau-ready dashboard CSVs

## Key Findings
- 62% of all late deliveries traced to 2 carrier routes (C001, C002)
- Peak periods (Nov-Jan) show significantly higher breach rates than rest of year
- Leinster region has highest order volume but breach rates vary significantly by carrier within region

## Recommendations
1. **Route reallocation:** Redistribute C001/C002 volume to C005-C010 during peak periods
2. **Peak staffing:** Increase capacity Nov-Jan based on historical breach pattern
3. **Lead-time buffers:** Add 1-day buffer for C001/C002 routes until performance improves
4. **Projected impact:** 1.2 day reduction in average delivery delay

## Tools
Python, SQL (DuckDB), pandas, matplotlib, seaborn, Tableau

## How to Run
```bash
pip install -r requirements.txt
python src/data_generation.py
python src/sql_analysis.py
python src/dashboard_export.py
jupyter notebook notebooks/eda_notebook.ipynb
```

## How to Explain in an Interview
- **Problem:** Ops team couldn't identify which carriers were causing SLA breaches
- **Data:** 100K synthetic orders, 18 months, 10 carriers, 4 regions
- **Approach:** SQL analysis via DuckDB, 7 visualisations
- **Finding:** 2 carriers responsible for 62% of all late deliveries
- **Impact:** 3 recommendations projected to reduce delay by 1.2 days
