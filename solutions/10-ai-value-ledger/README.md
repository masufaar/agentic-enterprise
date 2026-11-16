# AI Value Ledger

**Status: Designed. Not built yet.**

AI managed as an investment portfolio.

## What it is

A cost-and-benefit account for every agent in this repository: running cost, hours saved, cash impact and risk reduced, rolled up into a board dashboard.

## The management issue it solves

The company spends on AI and cannot say what it gets back.

## Why it matters to the business

Each agent has a profit-and-loss line. Agents that do not pay their way are stopped, and the budget moves to those that do.

## Agents

- Cost collection agent (model usage and infrastructure)
- Benefit measurement agent
- Board reporting agent

## Data needed

All data is synthetic and belongs to the fictional company described in [docs/company-profile.md](../../docs/company-profile.md).

- Usage and cost logs from every agent
- Benefit metrics defined in each business case
- Risk findings from the Control Tower

## Additional features planned

- Forecast of AI spend per business unit
- Model-tier optimisation advice per agent
- Comparison against external benchmarks

## Next steps

1. Define the common cost and benefit schema
2. Connect the first two built agents
3. Publish the first board dashboard

See the one-page [business case](BUSINESS_CASE.md).
