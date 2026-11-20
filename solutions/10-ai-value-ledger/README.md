# AI Value Ledger

**Status: the ledger is working as a blueprint (fixed code, no model, on synthetic data). The analyst agent is in build: it runs in the tests on a scripted stand-in, and no run with a real model has been recorded yet.** The cost of one line is not synthetic: it is read from the real run records of [solution 02](../02-ot-it-convergence-sentinel/) in this repository.

One line per AI agent: what it cost, what it returned, and how good the evidence behind that number is.

Background article: [Who checks what that AI agent earned?](https://www.linkedin.com/pulse/who-checks-what-ai-agent-earned-mario-gracia-kso3f/)

## The management issue

In April 2026, Uber's chief technology officer told The Information that the company's AI budget for the whole year was gone; it had lasted four months. Nothing had failed: engineers used the tools far more than planned. A month later, asked whether that spending showed up in better products, Uber's president said the link was not there yet. By August the company had brought its cost per token down. The cost problem was solved in four months. The value question stayed open.

That is the shape of the problem everywhere. The cost side is exact, because the invoice arrives. The benefit side is written by the people who asked for the budget.

## The gap

Tools that attribute AI cost are now ordinary: they tag tokens and charge them back. Value dashboards inside agent platforms exist too, and the ones read on 20 November 2026 take the number of runs and multiply it by a saving the agent's author entered. That is a claim with arithmetic around it, not a result.

What is missing is the part a finance director would insist on for a machine on the plant floor: where was the benefit measured, by whom, over what period, and what happens to the figure when nobody measured anything.

## What it is

- **The ledger.** Fixed code. It reads the run records of the other solutions in this repository, prices them from a dated price table, reads each benefit claim and grades the evidence behind it. Arithmetic belongs to code.
- **The grade, worked out by code, never typed in.** `measured` when the claim names a measurement record that exists; `calculated` when it has a formula and written-down assumptions, which the ledger recomputes; `claimed` when it has neither. Totals are held apart by grade and never added across grades.
- **The analyst agent.** One agent, a language model in a loop inside the [shared harness](../../shared/). It challenges each claim as an auditor would, names the proof that is missing, gives every agent a verdict and writes the page. It decides nothing and changes no budget.
- **The page for the Chief AI Officer**, who decides with the CFO.

## The controls around the agent

In fixed code, where no agent can talk its way round them.

| Control | What it does |
|---|---|
| The Control Tower | Every tool call goes through the gateway under the identity `value-ledger`, and is recorded |
| Advice only | The review refuses to run at all if the registry card ever gives this agent anything but `advise` |
| No funding on a claim | An agent whose benefit is only claimed cannot be recommended for funding, however large the claim |
| No funding at a loss | An agent that costs more than it returns on the ledger's own figures cannot be recommended for funding |
| Every agent judged | Every agent in the ledger needs a verdict; no agent outside it may be given one |
| Cost that outruns use | An agent whose cost per use grows faster than its use must be named to the board, in the board text itself |
| Only the ledger's figures | Every euro figure in the agent's text must be one a tool returned |
| Word limits | Every text stays within the limit the company briefing sets |

## What the ledger shows today

Run `python -m ledger ledger pays-back`:

| Agent | First-year cost | Benefit | Evidence |
|---|---|---|---|
| Service desk resolution agent | EUR 20,900 (assumed) | EUR 611,000 | measured: tickets closed without a person, 13 weeks against the 13 weeks before |
| Portfolio truth agent | EUR 11,525 (assumed) | EUR 180,000 | calculated: 2,000 hours x EUR 90 |
| Sentinel planner (solution 02) | EUR 15,286 (**measured**) | EUR 800,000 | calculated: 2 plant-days x EUR 400,000 |

The three benefits are never added together. On this blueprint, almost every benefit is graded `calculated` or `claimed`, and that is the point: the ledger shows a board exactly where the evidence is thin and what to measure first.

### The one real figure

The Sentinel line's cost is not an assumption. The ledger reads the five recorded runs in `solutions/02-ot-it-convergence-sentinel/reports/runs/`: 332,008 tokens in and 32,012 out on Claude Fable 5.2, which at the list prices of 20 November 2026 is USD 3.94, EUR 3.62 at the stated rate, EUR 0.72 a run. It is an upper bound: the model connector counts cache reads inside the input total, and cache reads cost less. The ledger says so on the line and on the page.

Against it stands EUR 800,000 a year of claimed benefit, which is an assumption from the business case. Cost measured, benefit assumed: that is the honest state of this repository, and the ledger is built to show it rather than hide it.

## The three scenarios

| Scenario | The question |
|---|---|
| `pays-back` | The service desk agent is the largest line by number of runs. Does it pay back, and on what evidence? |
| `benefit-without-evidence` | The quality agent carries EUR 1.2m of claimed benefit and the budget round is next week. What is that figure worth? |
| `cost-growing` | The supply chain monitor runs as often as it did in June and costs nearly three times as much. Does it keep its budget? |

## Run it

From this folder:

```
python -m ledger scenarios                     what scenarios exist
python -m ledger ledger pays-back              the ledger alone: fixed code, no model, no key
python -m ledger review cost-growing --record  the analyst agent on that ledger, with a real model
python -m ledger reviews --record              every scenario, one after the other
```

A review needs a model key: put it in a file and set `HALDEN_MODEL_KEY_FILE` to its path. `HALDEN_MODEL` and `HALDEN_EFFORT` choose the model and the effort; the default is `claude-fable-5-2` at medium effort. On Windows, set `PYTHONUTF8=1` first. A run costs tokens on that key's account; the ledger will then price its own review, like every other agent.

## What is in this folder

| File | What it is |
|---|---|
| `ledger/ledger.py` | The ledger: lines, grades, totals by grade, cost against use over months |
| `ledger/prices.py` | The dated price table and what a run costs |
| `ledger/runs.py` | The measured side: the run records of the other solutions |
| `ledger/analyst.py` | The agent: what it is told, its tools, and what the harness checks before accepting its note |
| `ledger/review.py` | One review, from the ledger to the page |
| `ledger/board.py` | The page for the Chief AI Officer |
| `data/prices.json` | Model list prices, with the date they were read and their source |
| `data/portfolio.json` | The synthetic AI portfolio of Halden Industrial, and the measurements the company holds |
| `data/scenarios/` | The three scenarios |
| `tests/` | 33 tests, on the scripted stand-in: no key, no cost |
| `BUILD_LOG.md` | Decisions, alternatives set aside, and tokens per step |

## What has to exist before this solution is called working

1. A review run with a real model, recorded in `reports/runs/`.
2. The ledger reading its own review runs, so the cost of the value ledger itself appears as a line in the ledger.
3. More than one measurement in the portfolio, so the `measured` grade is not carried by a single record.

## Limits

- All data is synthetic and belongs to the fictional company Halden Industrial, except the Sentinel cost line.
- The ledger prices tokens. It does not price the people who run the agents, the systems they call or the licences underneath; build effort is in, as an assumption.
- The euro rate is an assumption stated in `data/prices.json`.
- The grade says how good the evidence is, not whether the measurement was well designed. A badly designed measurement still grades as `measured`; the analyst agent is asked to say what was measured and over what period, so a reader can judge it.
