# S&OP Negotiation Arena

**Status: Designed. Not built yet.**

The monthly planning argument, run by agents, decided by people.

## What it is

Agents representing Sales, Finance, Operations and Procurement each argue their function's interest over inventory levels and production plans. A mediator agent sets out the trade-off for a human decision.

## The management issue it solves

Excess inventory ties up working capital while stock-outs still happen, and the monthly planning meeting is driven by positions more than by numbers.

## Why it matters to the business

Every function's argument is on the table with its numbers before the meeting starts. The outcome is expressed as cash released and service level kept, which is the language of the CFO.

## Agents

- Sales agent
- Finance agent
- Operations agent
- Procurement agent
- Mediator agent

## Data needed

All data is synthetic and belongs to the fictional company described in [docs/company-profile.md](../../docs/company-profile.md).

- Synthetic demand history and forecast
- Inventory by location and item class
- Capacity, service-level targets and carrying cost

## Additional features planned

- What-if runs during the live meeting
- Multi-echelon inventory positioning
- Link to the Supply Chain War Room for disruption-adjusted plans

## Next steps

1. Generate demand, inventory and capacity data
2. Define each agent's objective and constraints
3. Run three planning cycles and publish the trade-off memos

See the one-page [business case](BUSINESS_CASE.md).
