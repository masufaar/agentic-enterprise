# Supply Chain Disruption War Room

**Status: Designed. Not built yet.**

From a headline to costed options in minutes.

## What it is

Agents watch supplier news, tariffs, port congestion, weather and financial distress signals. Each event is mapped onto the bill of materials, the impact is simulated, and costed alternatives are proposed.

## The management issue it solves

Disruptions are discovered late and the response is improvised over email and spreadsheets.

## Why it matters to the business

The system moves from 'a supplier region is flooded' to 'these finished goods are at risk, here are three options with their margin impact' while there is still time to act.

## Agents

- Signal monitoring agents (news, logistics, weather, supplier finance)
- Bill-of-materials impact agent
- Scenario simulation agent
- Sourcing options agent

## Data needed

All data is synthetic and belongs to the fictional company described in [docs/company-profile.md](../../docs/company-profile.md).

- Synthetic bill of materials and supplier master
- Open event feeds or a recorded event set
- Lead times, inventory positions and margins per product

## Additional features planned

- Tariff scenario planner
- Supplier agent-to-agent enquiries for alternative capacity
- Carbon impact of each sourcing option

## Next steps

1. Build the synthetic bill of materials and supplier base
2. Replay five historical-style disruption events
3. Produce the options memo for each event

See the one-page [business case](BUSINESS_CASE.md).
