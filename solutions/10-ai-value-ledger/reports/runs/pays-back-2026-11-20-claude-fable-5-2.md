# AI Value Ledger: An agent that pays back: the service desk, with a measurement behind the benefit

For the Chief AI Officer, with the Chief Financial Officer. Prepared 2026-11-20. All data is synthetic (Halden Industrial), except the cost of agents marked measured, which is read from the run records in this repository.

**The question:** The service desk agent is the largest line of the AI budget by number of runs. Does it pay back, and on what evidence?

## The ledger

| Agent | First-year cost | Benefit | Owner |
|---|---|---|---|
| Service desk resolution agent | EUR 20,953 (assumed) | EUR 611,000 (measured) | Head of IT Operations |
| Portfolio truth agent | EUR 11,521 (assumed) | EUR 180,000 (calculated from assumptions) | Head of Transformation |
| Sentinel planner, plant cyber response | EUR 15,287 (measured) | EUR 800,000 (calculated from assumptions) | Head of OT Security |

First-year cost of these agents: EUR 47,761, of which EUR 15,287 is measured from run records.

Benefit, held apart by the evidence behind it, never added together:

- **Measured:** EUR 611,000 (sd-resolution)
- **Calculated from assumptions:** EUR 980,000 (portfolio-truth, ot-response)

## What the analyst recommends

| Agent | Recommendation | Why |
|---|---|---|
| Service desk resolution agent | fund | Benefit of EUR 611,000 is measured in the ticket system over 13 weeks against the 13 weeks before. First-year cost of EUR 20,953 is assumed, not measured. Fund, and record the real cost per ticket. |
| Portfolio truth agent | build the evidence | EUR 180,000 is a formula: 2,000 reporting hours saved, times an assumed hourly rate. Nobody has measured the hours. Cost of EUR 11,521 is also assumed. Not a result yet. |
| Sentinel planner, plant cyber response | build the evidence | Cost of EUR 15,287 is measured from five recorded runs. Benefit of EUR 800,000 is a formula: two plant days avoided, times an assumed revenue per plant day. No avoided stoppage has been recorded. |

**For the board, in the analyst's words:**

> The service desk agent pays back on the evidence we have. Its benefit of EUR 611,000 is measured: tickets closed without a person, in the ticket system, 1 July to 28 September 2026, against the same ticket types in the 13 weeks before. Its first-year cost of EUR 20,953 is an assumption; no run of this agent has been recorded. We recommend funding it and measuring its cost.
> The other two are not results yet. The portfolio reporting agent's EUR 180,000 rests on an assumed 2,000 hours saved. The plant cyber response agent's EUR 800,000 rests on an assumed two plant days avoided; its cost of EUR 15,287 is measured. We recommend building the evidence for both.
> These benefits are of different grades and are not added together. No month-by-month cost exists for any agent, so we cannot say whether cost is growing faster than use.

**What to measure first:**

> Record the service desk agent's actual runs and cost per ticket, month by month. It is the largest line by number of runs, its cost and its yearly volume of 46,000 runs are both assumptions, and no run is on record. Next: count the status reporting hours actually saved by the portfolio agent, since the assumed 2,000 hours carry its whole benefit.

**What nobody knows:**

> How tickets closed without a person were turned into euros, and whether EUR 611,000 covers 13 weeks or a full year. Whether closed tickets stayed closed. Whether the first three ticket types predict the rest. Whether the plant agent has ever avoided a stoppage. How any agent's cost moves as use grows.

## Behind every figure

**Service desk resolution agent** (sd-resolution)

- Cost, assumed: EUR 0.001 a run on claude-haiku-5-5, 46,000 runs a year (assumption), build 220 hours at EUR 95 an hour, = EUR 20,953 in the first year.
- No run records: the tokens per run are an assumption from the portfolio file.
- Benefit EUR 611,000, stated by the Head of IT Operations. Grade: measured. Measured: Tickets closed without a person, same ticket types as the 13 weeks before the agent. (Ticket system, Halden Industrial, 2026-07-01 to 2026-09-28).

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
- The ledger is fixed code. The analyst agent (claude-fable-5-2, effort medium) read: ot-response, portfolio-truth, sd-resolution.
- Agent turns: value-ledger 3 (handed in).
- Tokens: 14,178 in, 2,940 out. Seconds to this page: 25.56.
- Every step of the agent passed the AI Governance Control Tower under its own identity.
