# Business case: Self-Healing Service Desk

**Company:** Halden Industrial (fictional). **All figures are illustrative assumptions, not measured results.** Replace them with your own numbers.

## The problem

The service desk suite a company already runs now ships an agent that closes tickets without a person. Nobody independent checks that the problem is gone, for the right person, and that the record says what was done. Which ticket types the agent may close alone is decided on confidence, not on evidence.

## The proposal

In addition to the existing suite, never replacing it: a verifier agent that checks closed tickets and never closes one; an autonomy ladder that grants autonomy per ticket type on that evidence and takes it back at once when a check fails; and a resolution agent that works at the rung each ticket type has earned. Status: the ladder and the connector are working as fixed code; the two agents are designed.

## Value levers

| Lever | Assumption | Illustrative value |
|---|---|---|
| Ticket handling cost saved | 60,000 tickets x EUR 18 per ticket x 30% resolved without a person | EUR 324,000 |

The lever is counted per verified resolution, not per closed ticket: a ticket that comes back within seven days is not a saving.

Further benefits, not quantified here:

- The cost of one wrong reset. One manufacturer is claiming USD 380 million from its service desk provider over passwords reset for an unverified caller (Clorox v. Cognizant; the provider disputes the claim). No figure is assumed for Halden.
- More ticket types handed over, sooner, because each step is backed by evidence the company owns.
- Incidents that return become one permanent fix instead of many tickets.

## Cost

- **Build effort:** 40 to 60 hours for a thin working slice (estimate for one person working with an AI coding assistant).
- **Running cost:** not measured yet. It will be read from the recorded runs by the [AI Value Ledger](../10-ai-value-ledger/README.md) once the agents have run.

## Controls

Every agent in this solution is registered in the [AI Governance Control Tower](../01-ai-governance-control-tower/README.md), acts within written rules and is logged. The verifier holds no tool that changes a ticket. Plant-floor and security tickets are handed to the [OT/IT Convergence Sentinel](../02-ot-it-convergence-sentinel/README.md).

## Decision asked of the board

Confirm that the Head of IT Service Management decides which ticket types may be closed without a person, one rung at a time, on the verifier's evidence; and that identity-touching ticket types are never closed without a check.
