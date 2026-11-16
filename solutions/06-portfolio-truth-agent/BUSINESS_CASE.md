# Business case: Portfolio Truth Agent

**Company:** Halden Industrial (fictional). **All figures are illustrative assumptions, not measured results.** Replace them with your own numbers.

## The problem

Executives receive filtered, optimistic reporting and learn about failing projects too late.

## The proposal

Agents read project status reports, task systems and finance actuals. They flag projects whose reported status does not match the evidence, forecast slippage and suggest where capacity should move.

## Value levers

| Lever | Assumption | Illustrative value |
|---|---|---|
| Spend redirected earlier | EUR 40M yearly project portfolio x 5% | EUR 2M |

Further benefits, not quantified here:

- Earlier stop or rescue decisions
- Less time spent preparing status reports

## Cost

- **Build effort:** 40 to 60 hours for a thin working slice (estimate for one person working with an AI coding assistant).
- **Running cost:** Mid-tier model throughout; volumes are low.

## Controls

Every agent in this solution is registered in the [AI Governance Control Tower](../01-ai-governance-control-tower/README.md), acts within written rules and is logged. Actions with high impact wait for a named person.

## Decision asked of the board

Accept evidence-based status as the standard for the steering committee.
