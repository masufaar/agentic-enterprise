# Business case: AI Governance Control Tower

**Company:** Halden Industrial (fictional). **All figures are illustrative assumptions, not measured results.** Replace them with your own numbers.

## The problem

Agents are deployed faster than anyone counts them. When one misbehaves, nobody can say who approved it, what it may touch, or how many others exist. Accountability stays with management and the board.

## The proposal

A registry and control layer for AI agents. Every agent is registered with an owner, a purpose and a list of permitted systems. Every action is checked against company rules before it happens. Every decision is recorded in a tamper-evident trail. A dedicated red-team agent attacks the other agents every night and reports what it found.

## Value levers

| Lever | Assumption | Illustrative value |
|---|---|---|
| Audit documentation avoided | 100 agents x 6 h per quarter x 4 quarters x EUR 90/h | EUR 216,000 |

Further benefits, not quantified here:

- Faster approval of new agents (weeks, not months)
- Lower likelihood and lower impact of an agent incident
- Evidence ready for customers, auditors and insurers

## Cost

- **Build effort:** 135 to 195 hours (estimate for one person working with an AI coding assistant).
- **Running cost:** Policy enforcement is plain code and uses no model. A red-team campaign of 2,000 attacks costs roughly USD 5 on a small model tier and roughly USD 92 on a mid tier (estimate, list prices of late 2026).

## Controls

Every agent in this solution is registered in the [AI Governance Control Tower](../01-ai-governance-control-tower/README.md), acts within written rules and is logged. Actions with high impact wait for a named person.

## Decision asked of the board

Mandate that no AI agent goes live without registration in the control tower.
