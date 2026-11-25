# Business case: Supply Chain Disruption War Room

**Status: in build (25 November 2026).** See the [README](README.md) and [build log](BUILD_LOG.md).

**Company:** Halden Industrial (fictional). **The value levers below are illustrative assumptions, not measured results.** Replace them with your own numbers. One figure is measured from the synthetic data: a halt at the single source of part PCM-7 maps to four products with **EUR 1,143,000** of open customer orders at 12 days of cover (`python -m warroom trace supplier SUP-NORD`).

## The problem

Disruptions are discovered late and the response is improvised over email and spreadsheets.

## The proposal

Agents watch supplier news, tariffs, port congestion, weather and financial distress signals. Each event is mapped onto the bill of materials, the impact is simulated, and costed alternatives are proposed.

## Value levers

| Lever | Assumption | Illustrative value |
|---|---|---|
| Expedited freight reduced | EUR 6M yearly expedite spend x 10% | EUR 600,000 |
| Shortage stoppages reduced | 30 h per plant x 12 plants x EUR 15,000/h x 10% | EUR 540,000 |

Further benefits, not quantified here:

- Earlier customer communication on delivery risk
- Documented decisions for each disruption

## Cost

- **Build effort:** 60 to 80 hours for a thin working slice (estimate for one person working with an AI coding assistant).
- **Running cost:** Small model for signal filtering, mid-tier model for impact reasoning and the options memo.

## Controls

Every agent in this solution is registered in the [AI Governance Control Tower](../01-ai-governance-control-tower/README.md), acts within written rules and is logged. Actions with high impact wait for a named person.

## Decision asked of the board

Name one owner for disruption response across purchasing, logistics and sales.
