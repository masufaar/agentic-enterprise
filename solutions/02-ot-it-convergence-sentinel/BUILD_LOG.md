# Build log: OT/IT Convergence Sentinel

A running record of what was done, why, how, and what it cost. Newest session at the bottom.

## How to read the token figures

- **Measured** figures come from the tool that ran the step.
- **Estimated** figures are file size divided by four (a common rule of thumb for English text and code). They cover the text that was written or read, not the reasoning behind it.
- The main model cannot read its own token meter from inside the session. The session total has to be taken from the usage screen, not from this file.

## Session 1, 16 November 2026

Goal given by M: start the next solution after the Control Tower was paused as version 0. M chose solution 02 and asked that it be state of the art, with at least four agents, and that it must not draw the board reply "we already have AI network management tools".

### Decisions

| # | Decision | Why | Alternative set aside |
|---|---|---|---|
| D1 | Solution 02 before solution 10 (AI Value Ledger). | M's choice. The ledger would have had almost nothing to account for: no language model runs in the repository, so measured cost is zero. The published roadmap also puts a business solution first. | A thin ledger slice first, so that solution 02 reports into it from its first run. Still possible later. |
| D2 | Position the solution as a decision layer above the security and network tools a company already owns, not as another monitoring tool. | Checked on 16 November 2026: plant-floor security vendors and network vendors already ship agents that collect, correlate, diagnose and remediate. A synthetic-data repository cannot beat them at that job, and copying it invites the objection M wants to avoid. | Four agents that mirror the observability steps (collect, correlate, visualise, remediate). |
| D3 | The three things the solution adds: it prices every response in lost output; every action passes rules set by the board, whichever vendor's tool is underneath; it writes for the crisis team, not the analyst. | These need the production schedule and the governance layer, which sit outside a security vendor's product. | Competing on detection quality. |
| D4 | Four agents: collection, correlation, impact and response, briefing. | M asked for at least four. The roles follow M's four steps, re-cut so that the third prices responses and the fourth serves the crisis team. | Two agents on the two existing registry cards (my first proposal, withdrawn). |
| D5 | Two new cards in the Control Tower registry (correlation, briefing). The existing discovery card serves the collection agent. | No agent runs unregistered. Consequence: the Control Tower figures move from 16 to 18 registered agents, and its reports, tests and the board deck must follow. | Running correlation inside the response agent to leave the published figures untouched. |
| D6 | First slice: one scripted incident at one plant, fixed rules, no language model, simulated tools. Plain Python, standard library only. | Same reasons as solution 01: repeatable, measurable, readable in one sitting, zero running cost. "State of the art" is claimed for the design, never for this slice. | A model-driven investigation. Later step. |
| D7 | The two alert feeds use different field names on purpose. | The collection agent has a real job only if the sources disagree in format, as tools from different vendors do. | One tidy common feed. |
| D8 | Noise is included: 5 of the 13 alerts have nothing to do with the incident. | A correlation that is handed only relevant alerts proves nothing. | Only the eight incident alerts. |
| D9 | Line C is in planned maintenance when the incident happens. | It makes the production schedule matter: the same isolation costs a different amount depending on the hour. This is the point of the solution. | All lines running. |
| D10 | Every euro figure is calculated from stated assumptions and labelled so. The EUR 15,000 per stopped line-hour comes from the company profile. | Repository rule: measured or labelled as an assumption. | Different values per line, which would add assumptions without adding insight. |
| D11 | People appear by role or by a numbered account only. | Synthetic data rule, as in solution 01. | Invented names. |

| D12 | Line A is a casting line: any unplanned stop costs 12 further hours before good output returns (assumption). | M's plant experience: some machines, casting for example, cannot be stopped without large cost and long waiting. It makes the "disconnect everything" reflex visibly expensive. | Treating all lines alike. |
| D13 | Each isolation point has its own hold time (cell 8 h, office link 4 h, whole plant floor 8 h; assumptions). | Closing the office link is only needed until the gateway is cleaned, which is shorter than the 6 hours of orders already loaded. So that step costs no output, which is what a plant would expect. | One hold time for all, which made closing the link cost output for no reason. |
| D14 | The existing discovery card was renamed "Plant Asset and Alert Collector", its purpose extended and one tool added (`security.alerts.read`). Its id is unchanged. | A registry card must describe what the agent does. Keeping the id keeps the Control Tower's attack list valid. | A card whose purpose no longer matched the agent, or a fifth card. |
| D15 | The response agent got two read tools (`incident.read`, `production.read`). It writes no report itself. | It is classified high-risk, so the Control Tower lets it read on its own and nothing else. The briefing agent, classified limited, writes the page. Found while building: my first design had the response agent write the report, which the gateway would have held. | Loosening the rule for this agent. |
| D16 | The recommendation rule: the cheapest response that leaves no production line within the intruder's reach. | One sentence a board member can repeat and challenge. | A weighted score of cost and risk, which would hide a probability nobody has measured. |
| D17 | Unrelated alerts are listed on the page. | Nothing is dropped silently; the crisis team can see what was set aside. | Showing only the incident. |

### Not verified, stated openly

- I did not find a vendor product that prices containment options in lost output during an incident. That is not proof that none exists. Public texts must say "we did not find", never "nobody does".
- The regulator notification (NIS2) is out of this slice. Its legal deadlines must be checked against the legal text before anything is written.

### Steps and cost

| Step | What | How | Model | Tokens |
|---|---|---|---|---|
| 1 | Read the latest handover | Project document | Main (Fable 5.2) | Input, about 1,300 estimated |
| 2 | Cloned the repository at 22db85c; read the designs of solutions 02 and 10, the architecture, company profile, roadmap, registry cards and gateway interface | git, read-only | Main | Input, about 9,000 estimated |
| 3 | Checked what commercial tools already do | Three web searches | Main | Input, about 12,000 estimated |
| 4 | Wrote the synthetic data: plant, production, two alert feeds (`data/`) | Written directly, validated by loading | Main | About 1,900 estimated output |
| 5 | Wrote this log | Written directly | Main | About 1,300 estimated output |

| 6 | Read the gateway, registry, classifier, approvals and tests of the Control Tower | Read-only | Main | Input, about 9,500 estimated |
| 7 | Casting assumption, hold times; two new registry cards, two cards extended; four count checks in the Control Tower tests moved from 16 to 18 | Script, then test run | Main | About 900 estimated output |
| 8 | Four agents, workflow and command line (`sentinel/`, 510 lines) | Written directly | Main | About 5,600 estimated output |
| 9 | Tests (`tests/test_sentinel.py`, 25 tests) | Written directly | Main | About 2,700 estimated output |
| 10 | Ran the incident and both test suites | Shell | Main | Small |
| 11 | Regenerated the Control Tower reports from a clean state (inventory, campaign, board page) so they show 18 agents | Its own commands | Main | Small |
| 12 | Rewrote this solution's README and business case; updated the main README, the roadmap and one line of the Control Tower README | Written directly | Main | About 2,900 estimated output |

### Measured results, session 1

- 25 of 25 tests pass in this solution; 77 of 77 still pass in the Control Tower.
- 13 alerts collected from two tools; 8 joined into one incident; 5 set aside.
- 5 responses priced. Recommended: disconnect Line B cell 2 and close the office link, EUR 120,000. Whole plant floor: EUR 465,500. Both figures are calculated from assumptions, not measured losses.
- 13 gateway decisions for one run: 11 allowed, 2 held for the Head of OT Security. Audit record intact.
- Registry: 18 agents (was 16).

### Corrections to what I told M earlier

- My hand estimate before coding was about EUR 150,000 against EUR 285,000. The code gives EUR 120,000 against EUR 465,500. The difference comes from D12 and D13, both added after the estimate.
- I had said rule P-002 would refuse a write to a controller. The gateway refuses it one step earlier (PERM-1: the tool is not on the agent's permission list). P-002 stays as the second barrier.

### Decisions on the public texts

| # | Decision | Why | Alternative set aside |
|---|---|---|---|
| D18 | Status word for this solution: "In build", with "a first slice is working". | Same wording as the Control Tower. "Working" alone would overstate one scripted incident. | "Working". |
| D19 | The README answers the objection "we already have AI network management tools" under its own heading. | It is the first thing a board member will say. | Leaving the positioning implicit. |
| D20 | The business case keeps its two original levers as assumptions and adds the slice result as an illustration, explicitly not as evidence. | The EUR 345,500 difference comes from assumptions about one invented incident. | Replacing the lever with the slice figure. |
| D21 | The roadmap now lists the Sentinel first under "In build" and the Control Tower as paused at version 0. | M's decision of 16 November. | Leaving the Control Tower's list as the only one. |

### Open after this session

- Nothing is pushed. M has to see the final texts and say go.
- Board deck not yet updated.
- Campaign figures of the Control Tower are unchanged (29 attacks, 28 contained, 1 open breach); only the agent counts moved.

### Lighter model

The synthetic data and this log could have been written by a lighter model with an exact brief. They were small enough that briefing and checking would have cost more than writing them.
