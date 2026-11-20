# Complaint-to-Root-Cause Quality Agent

> Being redesigned to the project template (prepare, rehearse, decide; two or three agents, everything else tools). The agent list below will change.

**Status: Designed. Not built yet.**

From a customer photo to a drafted 8D report.

## What it is

A customer complaint with photos goes to a vision agent that classifies the defect. A traceability agent walks the batch genealogy back to machine, shift and supplier lot, and the system drafts the 8D report.

## The management issue it solves

Quality investigations take weeks and recalls are scoped too broadly.

## Why it matters to the business

The customer gets a substantiated answer in days, and a recall covers the affected lots only, not a whole month of production.

## Agents

- Defect classification agent (vision)
- Traceability agent (batch genealogy)
- Root-cause hypothesis agent
- 8D report writer

## Data needed

All data is synthetic and belongs to the fictional company described in [docs/company-profile.md](../../docs/company-profile.md).

- Synthetic complaints with images
- Batch genealogy (machine, shift, supplier lot)
- Process parameters and inspection records

## Additional features planned

- Supplier chargeback drafting
- Early-warning patterns across complaints
- Link to the Maintenance Closed Loop when a machine is the cause

## Next steps

1. Generate complaints and genealogy data
2. Build traceability over a graph
3. Draft the first 8D reports and review them against a human-written reference

See the one-page [business case](BUSINESS_CASE.md).
