# Business case: S&OP Negotiation Arena

**Company:** Halden Industrial (fictional). **All figures are illustrative assumptions, not measured results.** Replace them with your own numbers.

## The problem

Excess inventory ties up working capital while stock-outs still happen, and the monthly planning meeting is driven by positions more than by numbers.

## The proposal

Agents representing Sales, Finance, Operations and Procurement each argue their function's interest over inventory levels and production plans. A mediator agent sets out the trade-off for a human decision.

## Value levers

| Lever | Assumption | Illustrative value |
|---|---|---|
| Working capital released (one-off) | EUR 180M inventory x 5% | EUR 9M |
| Carrying cost saved per year | EUR 9M released x 8% carrying cost | EUR 720,000 |

Further benefits, not quantified here:

- Shorter, better-prepared planning meetings
- Transparent trade-offs between service and cash

## Cost

- **Build effort:** 50 to 70 hours for a thin working slice (estimate for one person working with an AI coding assistant).
- **Running cost:** Mid-tier model for the debating agents, top-tier optional for the mediator.

## Controls

Every agent in this solution is registered in the [AI Governance Control Tower](../01-ai-governance-control-tower/README.md), acts within written rules and is logged. Actions with high impact wait for a named person.

## Decision asked of the board

Agree one cash and service target that all four functions plan against.
