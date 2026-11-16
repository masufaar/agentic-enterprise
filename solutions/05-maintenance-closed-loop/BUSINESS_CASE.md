# Business case: Maintenance Closed Loop

**Company:** Halden Industrial (fictional). **All figures are illustrative assumptions, not measured results.** Replace them with your own numbers.

## The problem

Unplanned downtime, and expertise leaving the company with every retirement.

## The proposal

A sensor anomaly triggers a diagnosis agent that reads manuals and past work orders. Further agents check spare parts, find a low-cost production window and draft the work order. A side agent interviews retiring technicians by voice to capture their knowledge.

## Value levers

| Lever | Assumption | Illustrative value |
|---|---|---|
| Unplanned downtime reduced | 40 h per plant x 12 plants x EUR 15,000/h x 15% | EUR 1.08M |

Further benefits, not quantified here:

- Technician knowledge retained
- Fewer emergency spare-part orders

## Cost

- **Build effort:** 60 to 80 hours for a thin working slice (estimate for one person working with an AI coding assistant).
- **Running cost:** Small model for triage, mid-tier model for diagnosis.

## Controls

Every agent in this solution is registered in the [AI Governance Control Tower](../01-ai-governance-control-tower/README.md), acts within written rules and is logged. Actions with high impact wait for a named person.

## Decision asked of the board

Make maintenance, planning and spare parts share one schedule.
