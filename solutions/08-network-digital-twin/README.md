# Network Digital Twin

**Status: Designed. Not built yet.**

No change reaches a plant untested.

## What it is

A graph model of the global plant network. Agents perform root-cause analysis across sites and validate every configuration change in the twin before it reaches production.

## The management issue it solves

Outages caused by changes, and slow fault isolation across time zones.

## Why it matters to the business

A network change is rehearsed before it is made. The reliability statement a board can make is plain: no change reaches a plant untested.

## Agents

- Topology agent (keeps the twin current)
- Root-cause agent
- Change validation agent

## Data needed

All data is synthetic and belongs to the fictional company described in [docs/company-profile.md](../../docs/company-profile.md).

- Synthetic topology for 12 plants and 3 regions
- Configuration snapshots
- Event and incident history

## Additional features planned

- Capacity forecasting per site
- Automatic rollback plans
- Link to the OT/IT Sentinel for security-relevant changes

## Next steps

1. Model the network as a graph
2. Replay ten historical-style outages for root-cause analysis
3. Validate changes against the twin

See the one-page [business case](BUSINESS_CASE.md).
