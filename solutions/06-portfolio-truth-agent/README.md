# Portfolio Truth Agent

> Being redesigned to the project template (prepare, rehearse, decide; two or three agents, everything else tools). The agent list below will change.

**Status: Designed. Not built yet.**

Finds the projects that are green outside and red inside.

## What it is

Agents read project status reports, task systems and finance actuals. They flag projects whose reported status does not match the evidence, forecast slippage and suggest where capacity should move.

## The management issue it solves

Executives receive filtered, optimistic reporting and learn about failing projects too late.

## Why it matters to the business

The steering committee sees which projects need a decision this month, with the evidence attached, instead of a wall of green lights.

## Agents

- Status evidence agent
- Slippage forecast agent
- Capacity reallocation agent
- Steering-committee briefing writer

## Data needed

All data is synthetic and belongs to the fictional company described in [docs/company-profile.md](../../docs/company-profile.md).

- Synthetic project portfolio with status reports
- Task and milestone data
- Budget versus actuals

## Additional features planned

- Benefit tracking after go-live
- Dependency map across projects
- Vendor delivery performance

## Next steps

1. Generate a portfolio of 40 projects with hidden problems
2. Build the evidence-versus-status comparison
3. Produce the monthly steering briefing

See the one-page [business case](BUSINESS_CASE.md).
