# Build log: AI Value Ledger

What was decided while building this solution, why, and what was set aside. Tokens are estimated where no tool reported them.

## Session 1, 20 November 2026

Built from the plan in the project handover of 20 November 2026 (d): the ledger as fixed code, one analyst agent on the shared harness, three scenario files, one page for the Chief AI Officer, and the registry card from the existing designed card.

### Decisions

| | Decision | Why | Set aside |
|---|---|---|---|
| D1 | The ledger is fixed code; the only agent is the analyst that challenges the claims. | Arithmetic has one right answer and no language model should be between a board and it. The judgement, which claim is worth believing, is what an agent is for. | The three agents the page designed in September (collection, measurement, reporting): two of them were arithmetic dressed as agents. |
| D2 | The grade of a benefit is worked out by fixed code from the evidence that exists, never entered by the sponsor. | The whole failure this solution addresses is a number that nobody has to stand behind. If the sponsor could type in the grade, the ledger would repeat the failure with more ceremony. | A `grade` field in the portfolio file. |
| D3 | Three grades: measured, calculated, claimed. Totals are made per grade and there is no total benefit figure anywhere in the code. | A measured euro and a claimed euro are not the same money. A single total is the sentence a board remembers, so the code must not be able to produce one. | A weighted total, "risk-adjusted benefit". It would hide exactly what this solution exists to show. |
| D4 | A claim that names a measurement record which does not exist is graded `claimed`, not `measured`. | Naming a record is the cheapest way to look measured. | Trusting the name. |
| D5 | A claim with a formula is recomputed, and the formula wins over the stated figure if they disagree. | The formula is the thing that can be checked. | Reporting the stated figure with a warning. |
| D6 | The cost of a line is `measured` only when it comes from run records in this repository; otherwise `assumed`, and the line says so. | Same rule as for benefits, applied to our own side. | Treating a careful estimate as measured. |
| D7 | Every cost built from run records carries the note that cache reads are counted at the full input price, so the figure is an upper bound. | The connector sums plain input, cache writes and cache reads into one number (solution 02, D30 and the notes on tokens). Not saying so would overstate the cost and understate the care. | Estimating a cache-read share and quietly correcting the figure. |
| D8 | Prices come from a dated table with its source, not from constants in the code. | A board figure must be traceable to a price that was true on a day, and a company must be able to enter its contract prices without touching code. | Hard-coded prices. |
| D9 | A model with no price in the table stops the ledger. | A guessed price is worse than no figure. | Falling back to the most expensive model. |
| D10 | The review refuses to run if the registry card ever gives the analyst anything but `advise`. | This agent recommends on budgets. If someone widens its card, the right behaviour is to stop, not to run with more power than the design assumed. | Checking the briefing's decider against the card's owner, which was the check in solution 02. Here they are different roles on purpose: Finance answers for the agent, the Chief AI Officer decides on budgets. |
| D11 | The agent may not recommend funding an agent whose benefit is only claimed, or one that costs more than it returns on the ledger's figures. | These are the two decisions where a fluent argument is most likely to beat the evidence. | Letting the agent argue and marking the note. |
| D12 | An agent whose cost per use grows faster than its use must be named to the board in the board text itself, not only in a table row. | A rising cost per use is what nobody sees until the invoice arrives. A row in a table is not telling the board. | A flag on the page only. |
| D13 | Euro figures in the agent's text are checked against the figures the ledger produced, as in solution 02. | Same failure, same control: a model that writes a plausible number next to a real one. | Trusting the model to copy correctly. |
| D14 | The cost per run is written in cents on the page (EUR 0.72), but the agent writes only whole euro figures. | A per-run cost is well under a euro and rounding it to "EUR 1" would be wrong by 40 per cent. A board text works in whole euros. | One format everywhere. |
| D15 | The portfolio holds five agents; a scenario names the ones it reviews and may change a value. | Three scenarios with their own portfolios would drift apart. | A portfolio file per scenario. |

### What was checked

- Four test suites run in the assistant's workspace on Python 3.13: Control Tower 82, solution 02 92, shared harness 15, this solution 33. No test of another solution was changed except the two board figures below.
- `solutions/01-ai-governance-control-tower/data/agents.json`: the card `value-ledger` moved from `designed` to `agent in build`, with its name and purpose rewritten to what the agent does.
- That moved the Control Tower's board figures to 3 working, 1 in build, 6 fixed code, 10 designed; the test that counts them was updated, and the page now says "1 agent in build" rather than "1 agents in build".

### Tokens

| Step | What | How | Model | Tokens |
|---|---|---|---|---|
| 1 | Charter, handover, research note read; repository cloned and read (harness, Control Tower, solution 02) | Project documents, GitHub | Main (Opus 5) | Input about 90,000, output about 2,000, estimated |
| 2 | Data files, ledger, prices, runs, analyst, review, board page, command line | Written in the workspace | Main (Opus 5) | Output about 22,000, estimated |
| 3 | 33 tests written and run; Control Tower test and wording corrected | pytest | Main (Opus 5) | Output about 6,000, estimated |
| 4 | README, business case, this log | Written in the workspace | Main (Opus 5) | Output about 5,000, estimated |

A lighter model would have done step 1's reading and parts of step 4. The design decisions (D1 to D15) and the controls in `analyst.py` are the work that needed the main model.

## Session 2, 20 November 2026: the first real runs

Three reviews on Claude Fable 5.2 at medium effort, one per scenario, started by Mario with his own key. All three handed in a note the harness accepted: 3, 3 and 4 turns; 29.35, 33.08 and 41.78 seconds; 46,312 tokens in and 10,903 out together, EUR 0.74 at the list prices in `data/prices.json`.

The agent found two faults in the ledger it was given. Both are corrected here, and the corrected runs replace the first ones.

| | Decision | Why | Set aside |
|---|---|---|---|
| D16 | The cost of a run is kept at full precision; only the yearly figure and the page round it. | The analyst wrote that the service desk agent's running cost "is recorded as zero; that must be corrected". It was: EUR 0.00115 a run was rounded to EUR 0.00 and then multiplied by 46,000 runs. The cheapest models at the highest volumes are exactly where this matters. | Rounding at the unit and accepting the error as small. It was not small; it was the whole line. |
| D17 | The portfolio states what the agent does at the company; the registry card states what this repository has behind the blueprint. The tool shows both, named so they cannot be confused. | The analyst read the card's "designed" as "this agent never ran" and refused to recommend funding a benefit measured in the ticket system over 13 weeks. The question was right and the ledger's answer was ambiguous: a company can run an agent that this repository has only designed. | Changing the cards to say "working", which would have made this repository claim something it has not built. |

The first three runs are not kept: their figures came from the ledger before D16, so publishing them would publish the wrong numbers with the right reasoning. What the agent said about them is written down here and in the solution page.

**The published runs, after both corrections:** three reviews, 3, 4 and 4 turns; 25.56, 28.94 and 43.10 seconds; 55,538 tokens in and 10,899 out together, USD 0.88, EUR 0.81. The verdicts separate as the design intended: the service desk agent, the only measured benefit, is recommended for funding in all three; the quality agent's claim is refused funding by the harness rule and the agent explains why in its own words; the supply chain monitor is named to the board with its own figures. The card `value-ledger` moved to `agent working`, which took the Control Tower's counts to 4 working and 0 in build; its test followed.

### Tokens, session 2

| Step | What | How | Model | Tokens |
|---|---|---|---|---|
| 1 | Three real reviews | Mario's key, Fable 5.2 medium | Agent | 46,312 in, 10,903 out, measured |
| 2 | The two faults read out of the run records, both fixed, data model changed, tests extended to 34 | Workspace | Main (Opus 5) | Input about 25,000, output about 6,000, estimated |

### Open

- No run with a real model: the analyst agent is `in build` until a review is recorded in `reports/runs/`. Mario starts it with one PowerShell line.
- The ledger does not yet read its own review runs, so the value ledger has no line in the value ledger. That is the first thing to add after the real runs.
- The `measured` grade rests on one measurement record in the portfolio.

## Session 3, 23 November 2026: the service desk line is measured (step 8.2, solution 07, step 4c)

Solution 07 has 19 recorded agent runs on a real model. Its line in this ledger moves from an assumed cost to a measured one. No model ran in this session.

| | Decision | Why | Set aside |
|---|---|---|---|
| D18 | When a record lists its agent runs one by one, the ledger reads those runs and prices a stated unit of work (`runs.per_unit`). The Sentinel path, one file per use, is unchanged. | A solution 07 record is a scenario of four to six tickets worked by two agents. Counting files would have priced one scenario as one ticket, about five times too high. | Counting files; a second record format for solution 07. |
| D19 | The unit is one verified resolution: one run of the resolution agent plus the verifier's share of a check, 1.0 on the first day of the autonomy ladder (`act with check`). The share is data in the portfolio. | The article and the solution's business case commit to cost per verified resolution, not per closed ticket. The check is part of the cost of a closure the company can trust. | A separate line for the verifier: it has no benefit of its own and would read as pure cost. Per closed ticket. |
| D20 | The owner on the line and on the claim is the Head of IT Service Management, as on both registry cards. A test now checks the ledger's owner against the registry. | Open since solution 07's D15. The cards are the reference: their owner is in 82 Control Tower tests. | Renaming the cards to "Head of IT Operations". |
| D21 | The benefit is unchanged: the company's measurement of tickets closed without a person, graded measured. The page now says, on the line, what that measurement does not show; measuring verified resolutions is designed. | Changing the synthetic measurement to fit the article would be the after-the-fact adjustment solution 07's D46 refuses. The gap between closed and resolved is the article's point, and the page should show it. | Discounting the benefit by the verifier's findings in the scenarios: those flaws were planted on purpose and are not a rate. |
| D22 | The analyst's three recorded runs of 20 November are kept unchanged, with a note that they show the line as it was (EUR 20,953 assumed, owner "Head of IT Operations"). No new review was started. | A real run needs Mario's key. The records are evidence of what the agent was given that day. | Deleting or editing them. |
| D23 | A test pins that red-team records are never read as units of work. | Solution 07 keeps them in `reports/redteam/` for this reason (its D48); a test keeps it true if someone moves a file. | Relying on the folder alone. |

### What was measured

From the 19 agent runs in `solutions/07-self-healing-service-desk/reports/runs/`, Claude Fable 5.2 at medium effort, list prices read 20 November 2026, EUR 0.92 per USD (assumption):

- Resolution agent: 8 runs, 25,630 in and 1,376 out on average, EUR 0.24 a run.
- Verifier: 11 runs, 5,779 in and 764 out on average, EUR 0.07 a run.
- One verified resolution: EUR 0.31, an upper bound (cache reads at the full input price).
- At 46,000 tickets a year (assumption): EUR 14,257 of model cost, of which EUR 3,250 is the check. With 220 build hours at EUR 95 (assumption): EUR 35,157 in the first year, against EUR 20,953 assumed before. The rise comes from the model: the portfolio had assumed a small model at a tenth of a cent a run; the repository tests on Fable 5.2.

### What was checked

- Five suites: Control Tower 82, solution 02 92, shared harness 15, this solution 40 (34 plus 6), solution 07 79.
- Every figure written by hand on the pages was recomputed by the ledger's own code. The token totals agree with solution 07's build log: 268,617 in, 19,414 out.
- `reports/ledger-latest.md` generated again.

### Tokens

| Step | What | Model | Tokens |
|---|---|---|---|
| 1 | Charter, two handovers, solution 07 build log, ledger code, records read | Main (Claude Opus 5.5) | Input about 70,000, estimated |
| 2 | Ledger change, portfolio, 6 tests, pages of both solutions, roadmap, both logs | Main | Output about 16,000, estimated |

A lighter model could have updated the pages once the figures existed. Choosing the unit and keeping the benefit side honest was not work for a lighter model.

### Open

- A new review by the analyst agent, so a recorded run reads the measured service desk line. Done on 24 November, below.
- The measurement record for verified resolutions: designed.

### A review on the measured line, 24 November 2026

Mario ran `python -m ledger review pays-back --record`. Measured: 1 agent run, 5 turns, 27,172 tokens in and 3,842 out, 33.55 seconds, USD 0.37 at list price. Handed in and accepted. Verdicts: fund the service desk line; build the evidence for the other two. The agent carried the caveat of D21 into its text for the board without being asked to, and named the seven-day return rate as the first thing to measure. Copied into `reports/runs/` unchanged; searched for a key or an authorisation header: none. The three runs of 20 November stay as they are (D22).
