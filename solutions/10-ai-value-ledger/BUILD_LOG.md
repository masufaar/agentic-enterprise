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

### Tokens, session 2

| Step | What | How | Model | Tokens |
|---|---|---|---|---|
| 1 | Three real reviews | Mario's key, Fable 5.2 medium | Agent | 46,312 in, 10,903 out, measured |
| 2 | The two faults read out of the run records, both fixed, data model changed, tests extended to 34 | Workspace | Main (Opus 5) | Input about 25,000, output about 6,000, estimated |

### Open

- No run with a real model: the analyst agent is `in build` until a review is recorded in `reports/runs/`. Mario starts it with one PowerShell line.
- The ledger does not yet read its own review runs, so the value ledger has no line in the value ledger. That is the first thing to add after the real runs.
- The `measured` grade rests on one measurement record in the portfolio.
