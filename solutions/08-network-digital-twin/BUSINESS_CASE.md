# Business case: Network Digital Twin

**Company:** Halden Industrial (fictional). **All figures are illustrative assumptions, not measured results.** Replace them with your own numbers.

## The problem

Outages caused by changes, and slow fault isolation across time zones.

## The proposal

A graph model of the global plant network. Agents perform root-cause analysis across sites and validate every configuration change in the twin before it reaches production.

## Value levers

| Lever | Assumption | Illustrative value |
|---|---|---|
| Change-related outages reduced | 20 outages x 3 h x EUR 15,000/h x 30% | EUR 270,000 |

Further benefits, not quantified here:

- Faster fault isolation across time zones
- Auditable record of every change test

## Cost

- **Build effort:** 50 to 70 hours for a thin working slice (estimate for one person working with an AI coding assistant).
- **Running cost:** Mid-tier model for root-cause reasoning; validation is mostly deterministic.

## Controls

Every agent in this solution is registered in the [AI Governance Control Tower](../01-ai-governance-control-tower/README.md), acts within written rules and is logged. Actions with high impact wait for a named person.

## Decision asked of the board

Make twin validation a mandatory gate for network changes.
