# AI Value Ledger: An agent that pays back: the service desk, with a measurement behind the benefit

For the Chief AI Officer, with the Chief Financial Officer. Prepared 2026-11-23. All data is synthetic (Halden Industrial), except the cost of agents marked measured, which is read from the run records in this repository.

**The question:** The service desk agent is the largest line of the AI budget by number of runs. Does it pay back, and on what evidence?

## The ledger

| Agent | First-year cost | Benefit | Owner |
|---|---|---|---|
| Service desk resolution agent, with its verifier | EUR 35,157 (measured) | EUR 611,000 (measured) | Head of IT Service Management |
| Portfolio truth agent | EUR 11,521 (assumed) | EUR 180,000 (calculated from assumptions) | Head of Transformation |
| Sentinel planner, plant cyber response | EUR 15,287 (measured) | EUR 800,000 (calculated from assumptions) | Head of OT Security |

First-year cost of these agents: EUR 61,965, of which EUR 50,444 is measured from run records.

Benefit, held apart by the evidence behind it, never added together:

- **Measured:** EUR 611,000 (sd-resolution)
- **Calculated from assumptions:** EUR 980,000 (portfolio-truth, ot-response)

## What the analyst recommends

No agent ran: this page is the ledger alone, which is fixed code.


## Behind every figure

**Service desk resolution agent, with its verifier** (sd-resolution)

- Cost, measured: EUR 0.31 a verified resolution on claude-fable-5-2, 46,000 verified resolutions a year (assumption: tickets the agent works in a year, each checked once), build 220 hours at EUR 95 an hour, = EUR 35,157 in the first year.
- Measured from 19 agent runs in the run records of this repository (sd-resolution: 8 runs, 25,630 in and 1,376 out on average, 1 per verified resolution; sd-verifier: 11 runs, 5,779 in and 764 out on average, 1 per verified resolution). One verified resolution is one run of the resolution agent and one check by the verifier: on the first day of the autonomy ladder every closure is checked (solutions/07-self-healing-service-desk/data/ladder.json, 'act with check', share 1.0). A type that earns 'act alone' is checked on a 20% sample, which lowers this cost. Cache reads are counted at the full input price, so this is an upper bound.
- Run records read: 07-self-healing-service-desk/reports/runs/incident-returns-2026-11-23-claude-fable-5-2-run-b.json, 07-self-healing-service-desk/reports/runs/incident-returns-2026-11-23-claude-fable-5-2.json, 07-self-healing-service-desk/reports/runs/sound-batch-2026-11-23-claude-fable-5-2.json, 07-self-healing-service-desk/reports/runs/wrong-requester-2026-11-23-claude-fable-5-2.json.
- Benefit EUR 611,000, stated by the Head of IT Service Management. Grade: measured. Measured: Tickets closed without a person, same ticket types as the 13 weeks before the agent. (Ticket system, Halden Industrial, 2026-07-01 to 2026-09-28).
- What this measurement does not show: it counts tickets closed without a person, not tickets whose fix held. A closure that comes back within seven days is not a saving. Designed: from the next quarter the measurement record counts verified resolutions only, from the verifier's findings.

**Portfolio truth agent** (portfolio-truth)

- Cost, assumed: EUR 0.12 a run on claude-sonnet-5-5, 1,040 runs a year (assumption), build 120 hours at EUR 95 an hour, = EUR 11,521 in the first year.
- No run records: the tokens per run are an assumption from the portfolio file.
- Benefit EUR 180,000, stated by the Head of Transformation. Grade: calculated from assumptions. Calculated from stated assumptions: status_reporting_hours_saved 2,000 x hour_eur 90.

**Sentinel planner, plant cyber response** (ot-response)

- Cost, measured: EUR 0.72 a run on claude-fable-5-2, effort medium, 120 runs a year (assumption: rehearsed and real nights at 12 plants), build 160 hours at EUR 95 an hour, = EUR 15,287 in the first year.
- Measured from the run records of this repository. Cache reads are counted at the full input price, so this is an upper bound.
- Run records read: 02-ot-it-convergence-sentinel/reports/runs/new-alarm-after-plan-2026-11-19-claude-fable-5-2.json, 02-ot-it-convergence-sentinel/reports/runs/no-safe-response-2026-11-19-claude-fable-5-2.json, 02-ot-it-convergence-sentinel/reports/runs/plant-04-0302-2026-11-18-claude-fable-5-2.json, 02-ot-it-convergence-sentinel/reports/runs/plant-04-0302-2026-11-19-claude-fable-5-2.json, 02-ot-it-convergence-sentinel/reports/runs/plant-monitoring-down-2026-11-19-claude-fable-5-2.json.
- Benefit EUR 800,000, stated by the Head of OT Security. Grade: calculated from assumptions. Calculated from stated assumptions: plant_days_avoided 2 x revenue_per_plant_day 400,000.
- Source of the claim: solutions/02-ot-it-convergence-sentinel/BUSINESS_CASE.md.

## How this page was made

- Prices: Anthropic pricing page, platform.claude.com/docs/en/about-claude/pricing, read 20 November 2026; euro at 0.92 per USD (assumption).
- The analyst agent is registered in the Control Tower as advising only; the Head of Finance Business Partnering answers for it.
- The ledger is fixed code. The analyst agent (no agent ran) read: nothing.
- No agent ran.
- Tokens: 0 in, 0 out. Seconds to this page: 0.0.
- Every step of the agent passed the AI Governance Control Tower under its own identity.
