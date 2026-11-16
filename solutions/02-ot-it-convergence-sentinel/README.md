# OT/IT Convergence Sentinel

**Status: Designed. Not built yet.**

One security team of agents across the office network and the plant floor.

## What it is

A multi-agent security operations team. One agent discovers plant-floor assets passively, one correlates threats across office IT and operational technology, and one proposes responses that take production impact into account.

## The management issue it solves

Ransomware that stops production is the top cyber risk for a manufacturer, and the IT and plant security teams rarely share one picture.

## Why it matters to the business

Before recommending that a network segment be isolated, the response agent calculates what that isolation costs in lost output. Security decisions arrive in the language of production, and the incident notification for the regulator is drafted while the team works.

## Agents

- Asset discovery agent (passive, plant floor)
- Threat correlation agent (IT and OT events)
- Production-aware response agent
- Regulatory notification drafter (NIS2)

## Data needed

All data is synthetic and belongs to the fictional company described in [docs/company-profile.md](../../docs/company-profile.md).

- Synthetic network topology by plant and zone
- Synthetic security event stream
- Production schedule and hourly output value per line

## Additional features planned

- Mapping of agent permissions to IEC 62443 zones
- Tabletop exercise generator for the crisis team
- Supplier remote-access monitoring

## Next steps

1. Generate the synthetic plant network and event stream
2. Build the correlation agent on three attack scenarios
3. Add the production-impact calculation to each proposed response

See the one-page [business case](BUSINESS_CASE.md).
