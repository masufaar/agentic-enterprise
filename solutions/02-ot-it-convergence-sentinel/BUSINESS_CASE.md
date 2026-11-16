# Business case: OT/IT Convergence Sentinel

**Company:** Halden Industrial (fictional). **All figures are illustrative assumptions, not measured results.** Replace them with your own numbers.

## The problem

Ransomware that stops production is the top cyber risk for a manufacturer, and the IT and plant security teams rarely share one picture. In an incident the safe reflex is to disconnect everything, and nobody can say what that costs.

## The proposal

A decision layer above the security tools the company already owns. Four agents join the alerts of the office and plant-floor tools into one incident, price every possible response in lost output, and ask a named person to release the chosen one. The existing tools stay.

## Value levers

| Lever | Assumption | Illustrative value |
|---|---|---|
| Production protected | 2 plant-days of cyber-related stoppage avoided per year x EUR 400,000 revenue per plant-day | EUR 800,000 |
| Analyst time saved | 20,000 alerts x 10 min x 60% handled automatically x EUR 90/h | EUR 180,000 |

Further benefits, not quantified here:

- A response decision expressed in lost output, in front of the person who must take it
- One shared view for IT and plant security
- Regulatory notification deadlines met (designed, not built)

## What the first working slice adds to this case

In one scripted incident, the response the agents recommend costs EUR 120,000 in lost output and the "disconnect the whole plant floor" reflex costs EUR 465,500. The difference of EUR 345,500 for a single incident is calculated by the code from stated assumptions (EUR 15,000 per stopped line-hour, hold times, a casting line that is slow to restart). It is an illustration of the first lever, not evidence for it: no real incident has been measured. See [the page for the crisis team](reports/incident-latest.md).

## Cost

- **Build effort:** 60 to 80 hours for a thin working slice (estimate for one person working with an AI coding assistant). The first slice exists; its build record is in [BUILD_LOG.md](BUILD_LOG.md).
- **Running cost:** Zero for the first slice, which uses no language model. Designed: a mid-tier model for the investigation, a small model for the briefing.
- **Not included:** the licences of the security tools underneath, which the company already pays.

## Controls

Every agent in this solution is registered in the [AI Governance Control Tower](../01-ai-governance-control-tower/README.md), acts within written rules and is logged. Isolating any part of a plant network waits for the Head of OT Security. Measured in the first slice: 2 of 2 isolation requests held, none carried out without release.

## Decision asked of the board

Put IT and plant-floor security under one operating picture, and require that every containment decision is presented with its cost in lost output.
