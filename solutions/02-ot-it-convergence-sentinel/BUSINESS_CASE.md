# Business case: OT/IT Convergence Sentinel

**Company:** Halden Industrial (fictional). **All figures are illustrative assumptions, not measured results.** Replace them with your own numbers.

## The problem

Ransomware that stops production is the top cyber risk for a manufacturer, and the IT and plant security teams rarely share one picture.

## The proposal

A multi-agent security operations team. One agent discovers plant-floor assets passively, one correlates threats across office IT and operational technology, and one proposes responses that take production impact into account.

## Value levers

| Lever | Assumption | Illustrative value |
|---|---|---|
| Production protected | 2 plant-days of cyber-related stoppage avoided per year x EUR 400,000 revenue per plant-day | EUR 800,000 |
| Analyst time saved | 20,000 alerts x 10 min x 60% handled automatically x EUR 90/h | EUR 180,000 |

Further benefits, not quantified here:

- Regulatory notification deadlines met
- One shared view for IT and plant security

## Cost

- **Build effort:** 60 to 80 hours for a thin working slice (estimate for one person working with an AI coding assistant).
- **Running cost:** Mid-tier model for correlation and response reasoning, small model for alert triage.

## Controls

Every agent in this solution is registered in the [AI Governance Control Tower](../01-ai-governance-control-tower/README.md), acts within written rules and is logged. Actions with high impact wait for a named person.

## Decision asked of the board

Put IT and plant-floor security under one operating picture.
