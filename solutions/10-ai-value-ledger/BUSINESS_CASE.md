# Business case: AI Value Ledger

**Company:** Halden Industrial (fictional). **All figures are illustrative assumptions, not measured results**, except where this page says a figure is measured in this repository. Replace them with your own numbers.

## The problem

The company spends on AI and cannot say what it gets back. The cost side is exact, because the invoice arrives. The benefit side is written by the people who asked for the budget, and nobody has to show where it was measured.

## The proposal

One line per agent, under the AI Governance Control Tower: what it cost, read from its own run records, and what it returned, with the grade of the evidence behind that number. Benefits of different grades are never added together. An analyst agent, under the company's control, challenges each claim as an auditor would and names the proof that is missing. The Chief AI Officer and the CFO decide which agents keep their budget.

## Value levers

| Lever | Assumption | Illustrative value |
|---|---|---|
| AI budget redeployed from agents that cannot show a benefit to those that can | EUR 3M yearly AI spend x 10% | EUR 300,000 |

Further benefits, not quantified here:

- A factual answer to "what do we get for our AI spend?", with the evidence named
- Risk and return per agent on one screen, and a stop switch that already exists
- A budget round that argues about evidence rather than about confidence

## What the first version adds to this case

The ledger is fixed code and runs today. On the scenario `pays-back` it produces three lines: EUR 20,900, EUR 11,525 and EUR 15,286 of first-year cost, against EUR 611,000 of measured benefit and EUR 980,000 of calculated benefit, shown apart and never added.

One figure on it is measured, not assumed: the cost of the Sentinel planner of solution 02. The ledger reads the five recorded runs in that solution's `reports/runs/` folder: 332,008 tokens in and 32,012 out on Claude Fable 5.2, which at the list prices read on 20 November 2026 is USD 3.94, EUR 3.62 at the stated rate, EUR 0.72 a run. It is an upper bound, because the model connector counts cache reads at the full input price.

Against that measured cost stands the EUR 800,000 a year of this repository's Sentinel business case, which is an assumption with a formula. The ledger grades it `calculated` and prints the formula next to it. That is the honest state of the blueprint: cost measured, benefit assumed, and the page says which is which.

## Cost

- **Build effort:** 40 to 60 hours for a thin working slice (estimate for one person working with an AI coding assistant). The slice in this repository is the ledger, the analyst agent, three scenarios and the page.
- **Running cost:** one small model call per review. The ledger itself is ordinary data processing and uses no model.
- **Not included:** the finance systems the measurements come from, which the company already pays for.

## Controls

The analyst agent is registered in the [AI Governance Control Tower](../01-ai-governance-control-tower/README.md) as advising only, and the review refuses to run if that ever changes. Every tool call passes the gateway under the agent's identity and is recorded. The agent cannot recommend funding an agent whose benefit is only claimed, or one that costs more than it returns; it cannot write a euro figure the ledger did not produce; and an agent whose cost grows faster than its use must be named to the board. Measured in the tests: 33 of 33 checks pass, including each of those refusals.

## Decision asked of the board

Require a cost line and a graded benefit line for every AI agent in the company, and require that benefits of different grades are never added together in any paper that reaches the board.
