# Business case: OT/IT Convergence Sentinel

**Company:** Halden Industrial (fictional). **All figures are illustrative assumptions, not measured results.** Replace them with your own numbers.

## The problem

When an attack reaches the plant floor, the security tools say what is happening. Nobody can say what each response costs in lost production, or whether a smaller step would shut the intruder out just as well. The most expensive decision of the year is improvised at night, and the safe reflex wins: everything off.

## The proposal

AI agents under the company's control run that decision, not the detection, in addition to the existing security tools. In three stages:

- **Prepare.** The agents are briefed on the company as it is. Every possible response gets a price, per line and per shift.
- **Rehearse.** Simulated nights against the company's own landscape, so the crisis team practises the decision before it is real.
- **Decide.** In a real incident, one page reaches a named person within minutes: options, prices, the strongest counter-argument, and what the agents could not see.

Reversible steps on the office side are taken by the agents at once. Everything that touches the plant floor is decided by a named person.

## Value levers

| Lever | Assumption | Illustrative value |
|---|---|---|
| Production protected | 2 plant-days of cyber-related stoppage avoided per year x EUR 400,000 revenue per plant-day | EUR 800,000 |

Further benefits, not quantified here:

- A crisis team that has rehearsed the decision on its own plant
- Plants that can be connected with confidence, because an incident can be contained line by line
- An answer for customers and insurers who ask how an incident would be contained
- A record of who decided what, on which information

The earlier version of this case also counted analyst time saved on alerts (EUR 180,000). That benefit belongs to the detection tools, which this solution no longer claims, so it has been removed.

## What the rule-based first version adds to this case

In one scripted night, disconnecting the whole plant floor costs EUR 285,500 in lost production; a targeted response that shuts the intruder out just as well costs EUR 120,000. The difference of EUR 165,500 is calculated by fixed code from stated assumptions (EUR 15,000 per stopped line-hour and the hold times). It illustrates the lever; it is not evidence for it. No real incident has been measured, and no AI agent produced these figures.

## Cost

- **Build effort:** not yet estimated for the agents. The rule-based first version exists; its record is in [BUILD_LOG.md](BUILD_LOG.md).
- **Running cost:** zero today, because no language model runs. With agents there is a cost per rehearsed or real night, which will be measured and published with the first runs.
- **Not included:** the licences of the security tools underneath, which the company already pays.

## Controls

Every step of every agent passes the [AI Governance Control Tower](../01-ai-governance-control-tower/README.md): checked against written rules and recorded. A second agent challenges the first. Isolating any part of a plant network waits for the Head of OT Security. Measured in the rule-based first version: 2 of 2 isolation requests held, none carried out without release.

## Decision asked of the board

Name the person who decides whether a production line is disconnected, require that every response option is presented with its cost in lost production, and have that decision rehearsed before it is needed.
