# AI Value Ledger: Cost growing faster than use: the supply chain monitor

For the Chief AI Officer, with the Chief Financial Officer. Prepared 2026-11-20. All data is synthetic (Halden Industrial), except the cost of agents marked measured, which is read from the run records in this repository.

**The question:** The supply chain monitor runs as often as it did in June and costs nearly three times as much. Does it keep its budget?

## The ledger

| Agent | First-year cost | Benefit | Owner |
|---|---|---|---|
| Supply chain disruption monitor | EUR 19,618 (assumed) | EUR 240,000 (calculated from assumptions) | Head of Supply Chain |
| Service desk resolution agent | EUR 20,953 (assumed) | EUR 611,000 (measured) | Head of IT Operations |
| Complaint-to-root-cause quality agent | EUR 23,551 (assumed) | EUR 1,200,000 (claimed only) | Head of Quality |

First-year cost of these agents: EUR 64,122, of which EUR 0 is measured from run records.

Benefit, held apart by the evidence behind it, never added together:

- **Measured:** EUR 611,000 (sd-resolution)
- **Calculated from assumptions:** EUR 240,000 (disruption-monitor)
- **Claimed only:** EUR 1,200,000 (quality-traceability)

## What the analyst recommends

| Agent | Recommendation | Why |
|---|---|---|
| Supply chain disruption monitor | build the evidence | Benefit of EUR 240,000 is a formula, not a result: 8 disruptions caught early times an assumed cost of a late response. Neither number has a record. Monthly cost rose from EUR 1,104 to EUR 3,101 with flat use. |
| Service desk resolution agent | fund | Benefit of EUR 611,000 is measured in the ticket system, 1 July to 28 September 2026, against the 13 weeks before. First-year cost of EUR 20,953 is assumed, not yet taken from run records. |
| Complaint-to-root-cause quality agent | build the evidence | EUR 1,200,000 is the sponsor's statement only: no formula, no measurement set up. It is a claim, not a result. Not started; cost of EUR 23,551 is assumed. Agree a baseline before any funding. |

**For the board, in the analyst's words:**

> The supply chain monitor should not keep its budget unchanged. It ran 720 times in June and 736 in October. Its monthly cost went from EUR 1,104 to EUR 3,101. It reads more sources each run; nobody has shown this catches more disruptions. October alone cost about half the EUR 6,318 planned for a whole year of running. Its benefit of EUR 240,000 is calculated from two assumptions, not measured. We recommend building the evidence, not stopping it.
> The service desk agent has the only measured benefit: EUR 611,000, from the ticket system, over 13 weeks. We recommend funding it. Its cost of EUR 20,953 is still an assumption.
> The quality complaint agent has not started. Its EUR 1,200,000 is a claim with no formula and no measurement. We recommend no funding until a measurement is agreed.
> These benefit figures are of different grades and must not be added together.

**What to measure first:**

> For the supply chain monitor: count the disruptions it actually flagged early since 1 June 2026, and what a late response to each would have cost. The EUR 240,000 rests entirely on 8 such cases a year at an assumed cost each. In the same exercise, check whether the extra sources read since June produced any additional early warning. If they did not, cut them and the cost returns towards its June level.

**What nobody knows:**

> Whether the monitor has caught a single disruption early. Whether the EUR 611,000 is the 13-week result or a full-year projection of it. What any agent truly costs per run: all three budgets rest on assumed costs with no run records. The monitor's monthly cost series is marked synthetic in the ledger.

## Behind every figure

**Supply chain disruption monitor** (disruption-monitor)

- Cost, assumed: EUR 0.72 a run on claude-fable-5-2, 8,760 runs a year (assumption), build 140 hours at EUR 95 an hour, = EUR 19,618 in the first year.
- No run records: the tokens per run are an assumption from the portfolio file.
- Benefit EUR 240,000, stated by the Head of Supply Chain. Grade: calculated from assumptions. Calculated from stated assumptions: disruptions_caught_early 8 x cost_of_a_late_response 30,000.
- Cost per use, 2026-06 to 2026-10: use +2.2%, cost per run +174.8%. Cost is growing faster than use.

**Service desk resolution agent** (sd-resolution)

- Cost, assumed: EUR 0.001 a run on claude-haiku-5-5, 46,000 runs a year (assumption), build 220 hours at EUR 95 an hour, = EUR 20,953 in the first year.
- No run records: the tokens per run are an assumption from the portfolio file.
- Benefit EUR 611,000, stated by the Head of IT Operations. Grade: measured. Measured: Tickets closed without a person, same ticket types as the 13 weeks before the agent. (Ticket system, Halden Industrial, 2026-07-01 to 2026-09-28).

**Complaint-to-root-cause quality agent** (quality-traceability)

- Cost, assumed: EUR 0.31 a run on claude-opus-5-5, 2,400 runs a year (assumption), build 240 hours at EUR 95 an hour, = EUR 23,551 in the first year.
- No run records: the tokens per run are an assumption from the portfolio file.
- Benefit EUR 1,200,000, stated by the Head of Quality. Grade: claimed only. No measurement record and no formula: the figure is the sponsor's statement. Stated in the budget round as 'fewer recalls and faster root cause'. No formula was given and no measurement was set up.

## How this page was made

- Prices: Anthropic pricing page, platform.claude.com/docs/en/about-claude/pricing, read 20 November 2026; euro at 0.92 per USD (assumption).
- The analyst agent is registered in the Control Tower as advising only; the Head of Finance Business Partnering answers for it.
- The ledger is fixed code. The analyst agent (claude-fable-5-2, effort medium) read: disruption-monitor, quality-traceability, sd-resolution.
- Agent turns: value-ledger 4 (handed in).
- Tokens: 17,429 in, 3,141 out. Seconds to this page: 28.94.
- Every step of the agent passed the AI Governance Control Tower under its own identity.
