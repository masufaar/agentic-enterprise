# Business case: Self-Healing Service Desk

**Company:** Halden Industrial (fictional). **All figures are illustrative assumptions, not measured results.** Replace them with your own numbers.

## The problem

Slow support, repeated incidents and a high cost per ticket.

## The proposal

A ticket swarm of triage, resolution, change-risk and knowledge-writing agents, working in the languages of all sites. Every resolved ticket becomes a knowledge article automatically.

## Value levers

| Lever | Assumption | Illustrative value |
|---|---|---|
| Ticket handling cost saved | 60,000 tickets x EUR 18 per ticket x 30% resolved automatically | EUR 324,000 |

Further benefits, not quantified here:

- Faster resolution for employees
- A knowledge base that maintains itself

## Cost

- **Build effort:** 40 to 60 hours for a thin working slice (estimate for one person working with an AI coding assistant).
- **Running cost:** Small model for most tickets, mid-tier for complex cases.

## Controls

Every agent in this solution is registered in the [AI Governance Control Tower](../01-ai-governance-control-tower/README.md), acts within written rules and is logged. Actions with high impact wait for a named person.

## Decision asked of the board

Allow agents to resolve a defined list of ticket types without human hand-off.
