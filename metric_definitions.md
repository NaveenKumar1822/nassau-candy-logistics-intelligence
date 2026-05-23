# Metric Definitions

## Route Efficiency Score (RES)
Percentage of shipments delivered within SLA targets.

Formula:

RES = On-Time Shipments / Total Shipments

---

## Delay Magnitude
Number of days shipment exceeded SLA target.

Formula:

delay_magnitude = max(shipping_lead_time - sla_target, 0)

---

## Gross Margin %
Profitability percentage of fulfilled shipments.

Formula:

gross_margin_pct = gross_profit / sales