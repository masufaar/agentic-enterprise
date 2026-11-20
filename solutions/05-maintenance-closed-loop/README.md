# Maintenance Closed Loop

> Being redesigned to the project template (prepare, rehearse, decide; two or three agents, everything else tools). The agent list below will change.

**Status: Designed. Not built yet.**

From a sensor anomaly to a scheduled work order.

## What it is

A sensor anomaly triggers a diagnosis agent that reads manuals and past work orders. Further agents check spare parts, find a low-cost production window and draft the work order. A side agent interviews retiring technicians by voice to capture their knowledge.

## The management issue it solves

Unplanned downtime, and expertise leaving the company with every retirement.

## Why it matters to the business

Most predictive maintenance stops at the alert. This one ends with a scheduled action, a reserved part and a named technician, and it keeps the knowledge of the people who know the machines best.

## Agents

- Anomaly triage agent
- Diagnosis agent (manuals and work-order history)
- Spare-parts agent
- Scheduling agent
- Knowledge-capture interviewer

## Data needed

All data is synthetic and belongs to the fictional company described in [docs/company-profile.md](../../docs/company-profile.md).

- Synthetic sensor time series with labelled faults
- Equipment manuals (synthetic or openly licensed)
- Work-order history, spare-parts stock, production schedule

## Additional features planned

- Image-based inspection from a technician's phone
- Supplier warranty claims drafted automatically
- Energy-consumption anomalies

## Next steps

1. Generate sensor data for three machine types
2. Build diagnosis over manuals and work orders
3. Close the loop to a drafted work order

See the one-page [business case](BUSINESS_CASE.md).
