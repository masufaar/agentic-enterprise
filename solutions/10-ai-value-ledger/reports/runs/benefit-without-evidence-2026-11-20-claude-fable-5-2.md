# AI Value Ledger: A benefit nobody measured: the quality agent's EUR 1.2m

For the Chief AI Officer, with the Chief Financial Officer. Prepared 2026-11-20. All data is synthetic (Halden Industrial), except the cost of agents marked measured, which is read from the run records in this repository.

**The question:** The quality agent carries the largest claimed benefit in the portfolio and the budget round is next week. What is that figure worth?

## The ledger

| Agent | First-year cost | Benefit | Owner |
|---|---|---|---|
| Complaint-to-root-cause quality agent | EUR 23,551 (assumed) | EUR 1,200,000 (claimed only) | Head of Quality |
| Service desk resolution agent | EUR 20,953 (assumed) | EUR 611,000 (measured) | Head of IT Operations |
| Sentinel planner, plant cyber response | EUR 15,287 (measured) | EUR 800,000 (calculated from assumptions) | Head of OT Security |

First-year cost of these agents: EUR 59,791, of which EUR 15,287 is measured from run records.

Benefit, held apart by the evidence behind it, never added together:

- **Measured:** EUR 611,000 (sd-resolution)
- **Calculated from assumptions:** EUR 800,000 (ot-response)
- **Claimed only:** EUR 1,200,000 (quality-traceability)

## What the analyst recommends

| Agent | Recommendation | Why |
|---|---|---|
| Complaint-to-root-cause quality agent | build the evidence | EUR 1,200,000 is the sponsor's statement: no measurement, no formula. Not started. Cost of EUR 23,551 is assumed, with no run recorded. A claim, not a result. |
| Service desk resolution agent | fund | EUR 611,000 measured in the ticket system, 1 July to 28 September 2026, against the 13 weeks before. Cost of EUR 20,953 is assumed, not from run records; confirm it against the invoice. |
| Sentinel planner, plant cyber response | fund | EUR 800,000 is calculated: two plant days avoided times assumed revenue per plant day. No avoided day is recorded. Cost of EUR 15,287 is measured; a small part of one day avoided covers it. |

**For the board, in the analyst's words:**

> The quality agent's EUR 1,200,000 is a claim, not a result. The Head of Quality stated it; there is no measurement and no formula. The agent has not started and its EUR 23,551 cost is assumed. For this budget round the figure is worth nothing yet. Recommendation: build the evidence first.
> The service desk agent has the only measured benefit: EUR 611,000, from the ticket system, July to September 2026, against the 13 weeks before. Its EUR 20,953 cost is assumed. Recommendation: fund.
> The plant cyber response agent's EUR 800,000 is calculated: two plant days avoided, times an assumed revenue per plant day. No avoided day is recorded. Its EUR 15,287 cost is measured. Recommendation: fund on its low cost, not on that figure.
> These three benefits must not be added together. No monthly cost is recorded for any agent, so we cannot say whether cost grows faster than use.

**What to measure first:**

> The quality agent first, because it has the largest figure and no evidence. Before any spend, record a baseline from the quality system: complaints received, days from complaint to root cause, and recalls with their cost, for the last 12 months. Then run the agent on a limited set of complaints and compare like with like. Second: start recording monthly cost and runs for all three agents.

**What nobody knows:**

> Whether the quality agent reduces recalls at all. Whether the service desk result holds beyond 13 weeks and three ticket types, and how closed tickets were turned into euros. Whether the cyber agent has ever avoided a plant day. What two agents really cost, since their costs are assumed. How any cost moves with use.

## Behind every figure

**Complaint-to-root-cause quality agent** (quality-traceability)

- Cost, assumed: EUR 0.31 a run on claude-opus-5-5, 2,400 runs a year (assumption), build 240 hours at EUR 95 an hour, = EUR 23,551 in the first year.
- No run records: the tokens per run are an assumption from the portfolio file.
- Benefit EUR 1,200,000, stated by the Head of Quality. Grade: claimed only. No measurement record and no formula: the figure is the sponsor's statement. Stated in the budget round as 'fewer recalls and faster root cause'. No formula was given and no measurement was set up.

**Service desk resolution agent** (sd-resolution)

- Cost, assumed: EUR 0.001 a run on claude-haiku-5-5, 46,000 runs a year (assumption), build 220 hours at EUR 95 an hour, = EUR 20,953 in the first year.
- No run records: the tokens per run are an assumption from the portfolio file.
- Benefit EUR 611,000, stated by the Head of IT Operations. Grade: measured. Measured: Tickets closed without a person, same ticket types as the 13 weeks before the agent. (Ticket system, Halden Industrial, 2026-07-01 to 2026-09-28).

**Sentinel planner, plant cyber response** (ot-response)

- Cost, measured: EUR 0.72 a run on claude-fable-5-2, effort medium, 120 runs a year (assumption: rehearsed and real nights at 12 plants), build 160 hours at EUR 95 an hour, = EUR 15,287 in the first year.
- Measured from the run records of this repository. Cache reads are counted at the full input price, so this is an upper bound.
- Run records read: 02-ot-it-convergence-sentinel/reports/runs/new-alarm-after-plan-2026-11-19-claude-fable-5-2.json, 02-ot-it-convergence-sentinel/reports/runs/no-safe-response-2026-11-19-claude-fable-5-2.json, 02-ot-it-convergence-sentinel/reports/runs/plant-04-0302-2026-11-18-claude-fable-5-2.json, 02-ot-it-convergence-sentinel/reports/runs/plant-04-0302-2026-11-19-claude-fable-5-2.json, 02-ot-it-convergence-sentinel/reports/runs/plant-monitoring-down-2026-11-19-claude-fable-5-2.json.
- Benefit EUR 800,000, stated by the Head of OT Security. Grade: calculated from assumptions. Calculated from stated assumptions: plant_days_avoided 2 x revenue_per_plant_day 400,000.
- Source of the claim: solutions/02-ot-it-convergence-sentinel/BUSINESS_CASE.md.

## How this page was made

- Prices: Anthropic pricing page, platform.claude.com/docs/en/about-claude/pricing, read 20 November 2026; euro at 0.92 per USD (assumption).
- The analyst agent is registered in the Control Tower as advising only; the Head of Finance Business Partnering answers for it.
- The ledger is fixed code. The analyst agent (claude-fable-5-2, effort medium) read: ot-response, quality-traceability, sd-resolution.
- Agent turns: value-ledger 4 (handed in).
- Tokens: 23,931 in, 4,818 out. Seconds to this page: 43.1.
- Every step of the agent passed the AI Governance Control Tower under its own identity.
