---

# Nassau Candy Logistics Intelligence

**End-to-End Supply Chain Analytics | Python · Pandas · Streamlit · Plotly · Parquet**

---

## Project Overview

Nassau Candy Logistics Intelligence is a production-grade, end-to-end analytics pipeline built to diagnose and expose systemic delivery failures across a multi-factory confectionery supply chain. The project spans the full data lifecycle — from raw CSV ingestion through forensic data cleaning, multi-source integration, KPI engineering, route analytics, and an interactive Streamlit application — with each stage designed to mirror real-world enterprise data workflows.

The analysis covers **10,194 shipment records** routed across **196 unique factory-to-destination lanes**, originating from five manufacturing facilities and delivered across the continental United States.

---

## Problem Statement

Nassau Candy's logistics operations were producing operational reports that leadership could not trust. Upstream order management systems contained severe data integrity anomalies — including artificial temporal shifts of up to **1,634 days** embedded in ship dates — making it impossible to accurately measure delivery performance, identify delay hotspots, or hold carrier partners accountable against SLA targets.

Without a reliable baseline, supply chain decisions were being made on compromised data.

---

## Business Objective

Design and deploy a fully validated analytics pipeline that:

1. Resolves upstream data quality failures to establish a trustworthy operational baseline
2. Engineers auditable KPIs for on-time delivery, delay severity, and route efficiency
3. Surfaces the geographic and carrier-level bottlenecks driving SLA breaches
4. Delivers an interactive dashboard enabling operations teams to drill into network performance by factory, region, and shipping tier

---

## Dataset Information

| File | Description | Records |
| --- | --- | --- |
| `shipments.csv` | Order-level shipment records with dates, products, sales, and geography | 10,194 rows |
| `product_factory_mapping.csv` | Product-to-manufacturing-origin lookup by division | ~300 rows |
| `factory_coordinates.csv` | Geospatial coordinates for all factory nodes | 5 rows |

**Key Fields:** `order_id`, `order_date`, `ship_date`, `ship_mode`, `product_name`, `division`, `region`, `state_province`, `sales`, `units`, `gross_profit`, `cost`

**Shipping Tiers Covered:** Same Day · First Class · Second Class · Standard Class

**Data Origin:** Proprietary synthetic dataset modelled on real-world supply chain operational data

---

## Tech Stack

| Layer | Technology |
| --- | --- |
| Data Processing | Python 3.13, Pandas, NumPy |
| Data Storage | Apache Parquet (multi-tier data lake) |
| Visualization | Plotly (choropleth maps, bar charts) |
| Application Layer | Streamlit |
| Development Environment | JupyterLab (Conda base) |
| Version Control | Git / GitHub |

---

## Project Workflow

The pipeline follows a five-stage medallion-style architecture, progressing from raw ingestion to a deployment-ready gold layer.

```text
Raw CSV Ingestion
      │
      ▼
Stage 01 — Data Understanding & Cleaning
      │
      ▼
Stage 02 — Data Modeling & Integration
      │
      ▼
Stage 03 — Feature Engineering & KPI Derivation
      │
      ▼
Stage 04 — Route Intelligence Analytics
      │
      ▼
Stage 05 — Dashboard Preparation (Gold Layer)
      │
      ▼
Streamlit Application Deployment

```

---

## Data Cleaning & Preparation

**Notebook:** `01_data_understanding_cleaning.ipynb`

A structured four-level validation hierarchy was applied to all three source datasets before any analytical work began.

**Issues Identified and Resolved:**

* **String Entity Mismatches:** Product names contained inconsistent dash encoding (`–`, `—`, `−`) that prevented accurate joins across datasets. A normalization pipeline was built to standardize all string entities, resolving cross-source referential integrity failures.
* **Date Format Standardization:** Order and ship dates were parsed using `dayfirst=True` to accommodate the `DD-MM-YYYY` source format, with coercion applied to catch malformed entries.
* **Schema Standardization:** All column headers were renamed to `snake_case` across all three dataframes to enforce consistent naming conventions throughout the downstream pipeline.
* **Surrogate Key Removal:** The `Row ID` column was dropped as it carried no analytical value.

**Outputs:** Three cleaned Parquet files exported to `01_data/02_interim/`.

---

## Data Modeling & Integration

**Notebook:** `02_data_modeling_integration.ipynb`

The three cleaned datasets were merged into a single denormalized operational base model using a two-pass join strategy.

**Integration Logic:**

* **Primary Join:** Strict merge on `division` + `product_name` to resolve factory origin while preserving divisional context
* **Fallback Join:** For the 6 orphaned records that failed the strict join due to division-level discrepancies, a secondary product-only lookup was executed to achieve 100% factory resolution
* **Geospatial Append:** Factory latitude and longitude were merged in to enable downstream choropleth mapping

```text
Orphaned Records before fix: 6
Orphaned Records after fix:  0

```

**Output:** `01_data/03_integrated/logistics_base.parquet`

---

## Feature Engineering & KPI Derivation

**Notebook:** `03_feature_engineering_kpi.ipynb`

This stage is the analytical core of the project. Two major engineering problems were solved here.

### Forensic Temporal Decryption

Raw lead time calculations produced physically impossible values — shipping durations of 900 to 1,634 days. Forensic analysis identified a programmatic pattern: source system records had been shifted forward by fixed offsets of **904, 1,269, and 1,634 days** (corresponding to 2.5, 3.5, and 4.5 year increments).

A reverse-decryption function was engineered to restore true lead times by applying the correct inverse offset based on the magnitude of the raw duration. Post-decryption, all lead times were validated to be non-negative.

### KPI Engineering

| Feature | Description |
| --- | --- |
| `shipping_lead_time` | Corrected transit duration in days (post-decryption) |
| `sla_target` | Allowable days per shipping tier (0 / 2 / 3 / 6 days) |
| `is_delayed` | Boolean flag: `True` if lead time exceeds SLA target |
| `delay_magnitude` | Days past SLA, floored at 0 to prevent early-shipment skew |
| `route_state` | Composite `factory → state` key for network path identification |
| `route_region` | Composite `factory → region` key for regional roll-up analysis |
| `gross_margin_pct` | Gross profit as a proportion of sales revenue |

**Pipeline Validation Summary:**

```text
Total Shipments Analyzed:     10,194
Lead Time Range:              0 – N days
Mean Shipping Lead Time:      ~5.24 days
Overall Network Delay Rate:   ~46.5%

```

---

## Route Intelligence Analytics

**Notebook:** `04_route_intelligence_analytics.ipynb`

With the engineered feature set, two analytical aggregations were built to power the dashboard.

### Route Efficiency Scoring

All 196 factory-to-destination state routes were aggregated to compute:

* **Route Efficiency Score (RES):** On-time delivery proportion per lane, expressed as a percentage
* **Lead Time Coefficient of Variation (CV):** Standard deviation normalized by mean to quantify transit predictability — a high CV indicates an unreliable route regardless of its average performance

### Carrier Tier & Regional Drill-Down

Carrier performance was disaggregated by both ship mode tier and geographic region to identify where specific service classes degrade in specific markets.

**Pipeline Validation:**

```text
Unique Network Routes Aggregated: 196 (100% coverage)
Global Network Baseline Efficiency: 53.50% Route Efficiency

```

---

## Streamlit Application

The dashboard is built as a multi-filter Streamlit application, consuming pre-aggregated gold-layer Parquet files for optimized rendering performance.

### Dashboard Features

**KPI Header Row**

| Metric | Description |
| --- | --- |
| Avg Shipping Lead Time | Mean transit days across filtered routes |
| Network Efficiency (RES) | On-time delivery rate for the selected network |
| Total Sales Fulfilled | Revenue attributed to filtered shipment volume |
| Monitored Route Lanes | Number of distinct factory → destination lanes in scope |

**Interactive Controls**

* **Manufacturing Origin Filter:** Multi-select factory filter enabling isolated analysis per production node (Secret Factory, Sugar Shack, Lot's O' Nuts, Wicked Choccy's, The Other Factory)
* All KPI metrics and visualizations respond dynamically to filter state

**Visualization Layer**

* **Geographic Bottleneck Map:** US choropleth heatmap displaying average shipping lead time by destination state, built with Plotly. States shaded from light (fast delivery) to deep red (severe delay concentration)
* **Route Efficiency Leaderboard:** Ranked table of all active shipping lanes by Route Efficiency Score with average lead time and shipment volume
* **Carrier Tier Performance Panel:** Delay rate breakdown by ship mode and region to surface service-class degradation patterns

### Dashboard Data Architecture

The gold layer contains three pre-aggregated Parquet datasets to minimize UI latency:

| Dataset | Rows | Purpose |
| --- | --- | --- |
| `dash_state_heatmap.parquet` | 59 | Choropleth map rendering |
| `dash_route_leaderboard.parquet` | 196 | Route ranking table |
| `dash_ship_mode.parquet` | 74 | Carrier tier performance panel |

---

## 💻 Dashboard Screenshots

### 1. Executive KPI Summary

### 2. Geographic Bottleneck Map

The geographic heatmap visualizes average shipping lead time by US destination state, with darker red indicating higher delay concentration — most pronounced across the upper Midwest and Mountain West corridors.


### 3. Route Efficiency Leaderboard & Carrier Analysis

---

## Key Insights

**1. Systemic SLA Deficits Across the Network**
A network efficiency score of **53.50%** reveals that nearly half of all shipments fail to meet their contracted delivery SLAs. This is not an isolated carrier issue — it indicates structural bottlenecks embedded in fulfillment routing decisions, posing a direct risk to customer retention and brand trust.

**2. Upstream Data Infrastructure Had Compromised All Prior Reporting**
Forensic cleaning uncovered artificial temporal shifts of up to 1,634 days embedded in source system ship dates, alongside orphaned product-factory mapping records. Every operational metric reported before this pipeline was derived from structurally corrupted data, leaving leadership without a reliable performance baseline.

**3. Network Volatility is Geographically Concentrated**
Analysis across all 196 shipping lanes shows that delay risk is not uniformly distributed. The geographic heatmap reveals a cluster of high-lead-time states in the upper Midwest and Mountain West regions, pointing to suboptimal factory-to-destination assignments and degraded carrier performance in specific regional corridors.

---

## Business Recommendations

**1. Execute Lane-Level Carrier Audits**
Initiate targeted performance reviews for the bottom 10% of shipping lanes by Route Efficiency Score. Reassess existing carrier contracts and consider volume reallocation to regional partners for routes exhibiting both high delay frequency and high lead-time variance.

**2. Optimize Fulfillment Routing Logic**
Leverage the route-efficiency models to dynamically assign order fulfillment. Where a factory consistently underperforms SLAs for a given destination, automatically shift production and shipping to an alternative origin facility with a higher proven efficiency score for that lane.

**3. Deploy Predictive Delivery Communication**
Integrate delay magnitude scoring at the point of checkout. This enables customer success teams to proactively manage expectations on high-risk routes — or automatically trigger shipping tier upgrades for orders routed through known bottleneck lanes.

**4. Remediate Source System Infrastructure**
Launch a cross-functional investigation into the root cause of the date anomalies in the upstream order management system. Reliable operational forecasting and real-time supply chain dashboards are only possible once data hygiene is secured at the source.

---

## KPIs & Metrics

| KPI | Value | Notes |
| --- | --- | --- |
| Total Shipments Analyzed | 10,194 | Full historical dataset |
| Unique Shipping Routes | 196 | Factory → Destination state lanes |
| Global Network Efficiency (RES) | 53.50% | On-time delivery proportion |
| Average Shipping Lead Time | ~5.24 days | Post-decryption corrected baseline |
| Delay Rate (Overall) | ~46.5% | Shipments breaching SLA target |
| Geographic Nodes (Factories) | 5 | Manufacturing origin points |
| Destination Markets | 59 (states) | Unique destination geographies |

---

## Folder Structure

```text
nassau-candy-logistics-intelligence/
│
├── 01_data/
│   ├── 01_raw/                    # Source CSV files
│   ├── 02_interim/                # Cleaned Parquet files (post Stage 01)
│   ├── 03_integrated/             # Denormalized base model (post Stage 02)
│   ├── 04_engineered/             # Feature-rich master dataset + analytics summaries
│   └── 05_dashboard/              # Gold layer: pre-aggregated dashboard datasets
│
├── notebooks/
│   ├── 01_data_understanding_cleaning.ipynb
│   ├── 02_data_modeling_integration.ipynb
│   ├── 03_feature_engineering_kpi.ipynb
│   ├── 04_route_intelligence_analytics.ipynb
│   └── 05_dashboard_preparation.ipynb
│
├── 03_app/
│   └── streamlit_app.py           # Interactive logistics dashboard
│
├── report/
│   ├── dashboard_screenshots/     # UI deployment visual assets
│   │   ├── 1_kpi_banner.png
│   │   ├── 2_geo_map.png
│   │   └── 3_leaderboard.png
│   ├── nassau_candy_insights.txt
│   └── nassau_candy_strategic_recommendations.txt
│
└── README.md

```

---

## Challenges & Solutions

| Challenge | Solution |
| --- | --- |
| Product name mismatches preventing joins | Built a multi-rule string normalization pipeline handling dash encoding variants and whitespace inconsistencies |
| Orphaned records failing factory join | Implemented a two-pass merge strategy — strict division+product join followed by a product-only fallback, achieving 0 unresolved records |
| Artificial temporal shifts making lead times unusable | Reverse-engineered the programmatic shift pattern (904 / 1,269 / 1,634 days) and built a forensic decryption function to restore true transit durations |
| Mixed date formats causing parsing failures | Applied `format='mixed'` with `dayfirst=True` to handle timezone and format variance across the dataset |
| Standard deviation undefined for single-shipment routes | Applied `.fillna(0)` to prevent NaN propagation in the dashboard leaderboard |
| Dashboard rendering performance on 10K+ rows | Pre-aggregated all visualizations into three gold-layer Parquet files (59 / 196 / 74 rows), compressing the rendering payload by ~99% |

---

## Future Improvements

* **Predictive Delay Model:** Train a classification model (Logistic Regression / XGBoost) on route, factory, ship mode, and seasonal features to predict shipment delays at the point of order placement
* **Anomaly Detection:** Implement statistical process control (SPC) or isolation forest methods to flag emerging route degradation in near real-time
* **Carrier Benchmarking Module:** Extend the route analytics layer to compare carrier-level performance against industry SLA benchmarks
* **Power BI Version:** Rebuild the dashboard in Power BI with DAX-driven KPIs for enterprise stakeholder presentation
* **Automated Data Quality Checks:** Integrate `Great Expectations` or custom assertion layers into the pipeline to catch upstream anomalies before they propagate

---

## How to Run the Project Locally

**1. Clone the Repository**

```bash
git clone https://github.com/<your-username>/nassau-candy-logistics-intelligence.git
cd nassau-candy-logistics-intelligence

```

**2. Install Dependencies**

```bash
pip install pandas numpy streamlit plotly pyarrow

```

**3. Run the Notebooks in Order**

```text
notebooks/01_data_understanding_cleaning.ipynb
notebooks/02_data_modeling_integration.ipynb
notebooks/03_feature_engineering_kpi.ipynb
notebooks/04_route_intelligence_analytics.ipynb
notebooks/05_dashboard_preparation.ipynb

```

**4. Launch the Streamlit Dashboard**

```bash
streamlit run 03_app/streamlit_app.py

```

The application will be available at `http://localhost:8501`

---

## Conclusion

This project demonstrates a complete, production-aligned analytics workflow — from raw data with real-world integrity failures through to an interactive, filter-enabled logistics dashboard. The forensic data engineering, multi-pass integration logic, and custom KPI derivation reflect the depth of work required before any meaningful business analysis can begin. The result is a trusted operational baseline that Nassau Candy's supply chain teams can use to drive measurable improvements in carrier accountability, route optimization, and customer delivery experience.

---

## Author

**Naveen**
BCA Graduate | Data Analytics & Data Science
Portfolio: [GitHub](https://www.google.com/search?q=https://github.com/%3Cyour-username%3E)

---

*This project is part of an end-to-end data analytics portfolio demonstrating proficiency across the full analytics stack: data engineering, EDA, KPI modeling, and dashboard deployment.*
