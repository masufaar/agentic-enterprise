# OT/IT Convergence Sentinel

**Status: Working as a blueprint. Three agents run on a real model, on synthetic data, with five recorded runs (18 and 19 November 2026); not connected to real systems.** The runs cover the scripted night, a night on which no response closes every path, a night with the plant-floor monitoring down, and a night in which a new alarm arrives after the first plan. Five runs are five runs: each night has run once, so no rate can be stated. Still designed: a scenario agent that invents rehearsal nights, and a connector for a second model provider.

It runs the decision, not the detection, in addition to your existing tools.

Background article: [Who decides to stop the plant?](https://www.linkedin.com/pulse/who-decides-stop-plant-mario-gracia-blhnf/)

## The management issue

In September 2025, Jaguar Land Rover shut down its systems to contain a cyber attack. No car left its three UK plants for more than five weeks, and the Cyber Monitoring Centre put the cost to the British economy at GBP 1.9 billion, across more than 5,000 organisations ([report coverage](https://www.computerweekly.com/news/366633395/Jaguar-Land-Rover-attack-to-cost-UK-19bn-say-cyber-monitors)). The attackers did not stop those plants; the company did, to protect itself. The moment worth studying is the one before: a few people, at night, deciding how much of their company to switch off.

Take that moment to Halden Industrial, the fictional manufacturer of this repository. At 02:10 someone in finance opens an infected attachment. By 02:44 the intruder sits at the computer that programs Line B. At 03:02 he is looking for a way into Line C. The security tools did their job: every step raised an alarm. The plant manager asks the only question that matters: "If we disconnect, what do we lose?" Nobody knows.

## The gap

Manufacturers have invested for years in seeing attacks, and it works. But no security tool is built to hold the production plan, the open orders or the cost of an hour of standstill. So the most expensive decision of the year is improvised, and the safe reflex wins: everything off.

## What it is: three stages

AI agents under the company's control run that decision.

- **Prepare.** The agents are briefed on the company as it is: its tools, plant layout, production plan and rules. Every possible response gets a price, per line and per shift.
- **Rehearse.** Simulated nights against the company's own landscape. The crisis team practises the decision before it is real.
- **Decide.** In a real incident, one agent builds the response, a second attacks it, and one page reaches a named person within minutes: the options, their prices, the strongest counter-argument, and what the agents could not see.

## In addition to your existing tools

| Layer | What it does | Whose job | At Halden (invented names) |
|---|---|---|---|
| Plant-floor monitoring | Knows the machines and controllers; raises alarms on the plant network | Your existing tools | Corvane OT Watch |
| Office security | Watches computers, accounts and email | Your existing tools | Brightmoor Endpoint |
| Investigation across both | Joins the alarms and traces the intruder's path, often with AI agents | Your existing tools | Varrick SOC Agents |
| Network separation | Carries out a disconnection | Your existing tools | Tessgate Firewalls |
| **The decision** | What each response costs in lost production, which one to take, who decides, and the record of it | **This solution** | |

The solution takes the findings of those tools as its input. It does not replace them and does not try to detect better than they do. The vendor names in the last column are invented for the fictional company; a web search on 20 November 2026 found no security product under these names. In the repository, the first two of these tools are simulated by alarm files (`data/events_plant.json`, `data/events_office.json`).

## Why agents, and not one more piece of software

- **Customized.** The agents are briefed on a company, not programmed for it. A new tool, a new line or a new rule changes the briefing, not the code. They say what they were not given.
- **Adapting.** When the night changes (a new alarm, a line starting its shift, a step that fails) they plan again from the new facts.
- **Learning.** Every incident, decision and outcome is kept. The next incident, real or rehearsed, starts from what the last one taught. Changes to the standing playbook are proposed by an agent and approved by a person.
- **Controlled.** Agents can be wrong. So one challenges the other, a person decides, and every step passes the [AI Governance Control Tower](../01-ai-governance-control-tower/README.md): checked against the company's rules and recorded.

## The responses, and who may take them

The options go far beyond "stop the line".

| Kind of step | Examples | Who acts |
|---|---|---|
| Office side, reversible | Suspend an account, end a remote session, withdraw one supplier's remote access | The agents, at once, under the company's rules |
| Between office and plant | Close the remote gateway; run the plant as an island on the orders already loaded | A named person |
| Plant floor | Isolate one cell; stop one line; disconnect the whole plant floor | A named person |
| Production measures | Move an urgent order to another line; bring planned maintenance forward into the stop | A named person |

No agent disconnects anything on the plant floor. This list is a design and will be corrected against plant practice.

## What exists today

Stated on 19 November 2026. "Tested on prepared replies" means: the code around the model is tested with a stand-in that replays replies written by hand. That proves the loop and the controls. It does not prove that a model reasons well; only recorded real runs can. Five exist; they are described in the next sections.

| Building block | Status | Model involved |
|---|---|---|
| Model of one plant and its production plan (synthetic files) | Working | No |
| Price of a response in lost production, from the plan | Working, fixed code; now a tool the agents call | No |
| Hold of every plant-floor step for the Head of OT Security, through the Control Tower | Working, fixed code | No |
| Joining the alarms of two simulated tools into one incident | Working as a basic fixed rule | No |
| Agent loop: the model asks for tools, a failed or refused step is handed back to it, and it is finished only when the harness accepts its result | Working: 13 hand-ins handed back and corrected by the model in the runs of 19 November | Yes, 5 runs |
| Model connector: one neutral format, a connector for Claude | Working for Claude. A connector for a second provider is designed | Yes, 5 runs |
| Company briefing that the agents read | Working: read by a model in 5 runs. Not yet shown with a model: a changed briefing changing behaviour (tested on prepared replies) | Yes, 5 runs |
| First-response agent: reversible office-side steps on its own | Working: 5 runs, every step within the briefing, none attempted on the plant floor | Yes, 5 runs |
| Planner agent and challenger agent, with objection and answer | Working: the challenger objected in 1 of 5 runs and the planner answered; it agreed in 4 | Yes, 5 runs |
| A night on which no response closes every path | Working: one run; the page says so in plain words | Yes, once |
| Decision page with options, prices and counter-argument; the named person's choice recorded | Working: 5 pages from real runs. The choice is tested on prepared replies; it was not made after the real runs | Yes, 5 runs |
| Blind spots when a security tool is missing: the page names the tool, and the lines it would have watched are never priced as safe | Working: one run | Yes, once |
| A new alarm after the first plan: every price is out of date, the planner plans again, the page shows the plan before and after | Working: one run; the plan changed | Yes, once |
| Case memory: each night recorded as a case, the named person's decision and note added, earlier cases read by planner and challenger through the Control Tower | Working: read by the agents in 3 runs. Those cases carried no decision yet; a decision and note are tested on prepared replies. Lessons are written by the named person, not by an agent; an agent may propose a change to the briefing, which a person applies or not | Yes, 3 runs |
| Word limit per field, enforced at hand-in | Working: every text on the 19 November pages is within its limit, after correction | Yes, 4 runs |
| Rehearsal: a scenario agent that invents nights from the briefing | Designed. For now, the nights in `data/nights/` are written by hand | |

A sample of the decision page, produced on prepared replies and labelled as such: [reports/decision-page-sample-scripted.md](reports/decision-page-sample-scripted.md).

In this project the word agent is reserved for a language model working in a loop with tools, checking and correcting its own result. Three such agents are in build here: first response, planner, challenger. The joining of alarms and the writing of the page are fixed code; they hold registry cards in the Control Tower because they act through its gateway, and the registry says of each card what stands behind it.

## The recorded runs of 19 November 2026

Measured on 19 November 2026: four nights, one run each, Claude Fable 5.2 at medium effort, started with `python -m sentinel nights --record`, one after the other, with the case memory on. Each page and the full record of every turn are in [reports/runs/](reports/runs/). Each night ran once: these are observations, not rates.

| Night | Page | Recommended | Challenger | Seconds to page | Tokens in / out |
|---|---|---|---|---|---|
| Scripted night | [page](reports/runs/plant-04-0302-2026-11-19-claude-fable-5-2.md) | Line B, cell 2 and the office link, EUR 120,000; no line left within reach | Agrees | 61.40 | 77,969 / 5,635 |
| New alarm after the first plan | [page](reports/runs/new-alarm-after-plan-2026-11-19-claude-fable-5-2.md) | Before the alarm: EUR 120,000. After it: the whole plant floor, EUR 287,250 | Agrees | 77.79 (43.01 from the new alarm) | 85,851 / 7,460 |
| No response closes every path | [page](reports/runs/no-safe-response-2026-11-19-claude-fable-5-2.md) | Line B, cell 2 and the office link, EUR 120,000; Line C stays within reach, EUR 720,000 at stake, said in plain words | **Objects**; the planner keeps its steps and answers | 77.48 | 88,316 / 7,451 |
| Plant-floor monitoring down | [page](reports/runs/plant-monitoring-down-2026-11-19-claude-fable-5-2.md) | Close the office link, EUR 0; Lines A, B and C not watched, EUR 2,160,000 at stake; the planner writes "This recommendation is not a safe one" | Agrees | 49.73 | 44,530 / 4,561 |

Over the four nights:

- Every one of the 14 agent runs ended with a result the harness accepted.
- 13 hand-ins were handed back and corrected by the model, all for a text over its word limit. None was handed back for a figure the pricing tool had not produced. The Control Tower refused no step.
- The first-response agent took the same four office-side steps every night, all within the briefing; it attempted nothing on the plant floor.
- The debate: on the night with no safe response, the challenger agreed with the steps and objected to two gaps on the page: the EUR 0 of the link closure holds only if the link reopens within the six-hour order buffer, and nobody had set a decision on whether Line C restarts at 08:00. The planner checked both, kept its steps and added both to the page.
- The new alarm: 43.01 seconds after it arrived, the page showed the plan before (EUR 120,000) and the changed plan (EUR 287,250), with the reason.
- The case memory: from the second night on, planner and challenger read the earlier cases through the Control Tower and said whether they changed their view. None did; those cases carried no decision yet.
- Three proposed changes to the company briefing, recorded and not applied. Twice: add a step that disconnects Line C, cell 1 alone, and close the old file share between Line B and Line C, so that a narrow stop is possible next time. Once, on the blind night: when the plant-floor monitoring is down, a person on site checks the cells by hand before a narrow response is treated as enough.

What these runs show that a board should know, and the fix designed for each:

- **The harness makes a risk visible; it does not choose for the decider.** On the blind night the agents recommended the EUR 0 response and stated that it is not safe, with EUR 2,160,000 unwatched. The only response that rules anything out costs EUR 279,500. That choice belongs to the Head of OT Security, and the page puts it in front of that person. The briefing change proposed by the planner is the designed fix: a check by hand on site, decided by a person.
- **The agents write up to the word limit.** The texts are shorter than on 18 November but still dense for three in the morning. Fix designed: lower limits in the briefing, a change to one file.
- **Each night ran once.** No rate can be stated. Fix designed: the same four nights run again, and a changed briefing run once to show that it changes behaviour.

## The first run with a real model, 18 November 2026

Measured on 18 November 2026: one run of the scripted night, Claude Fable 5.2 at medium effort, started with `python -m sentinel night --record`. The page as produced: [reports/runs/plant-04-0302-2026-11-18-claude-fable-5-2.md](reports/runs/plant-04-0302-2026-11-18-claude-fable-5-2.md); the full record of every turn is the `.json` file beside it. One run is one run: no rate can be stated from it.

| Measure | Result |
|---|---|
| Agents that handed in a result the harness accepted | 3 of 3 |
| Results the harness handed back for correction | 0 |
| Time from the last alarm handed over to the decision page | 71.62 seconds |
| Tokens | 35,342 in, 6,905 out |
| Responses priced by the agents | 8 |
| Office-side steps taken by the first-response agent on its own | 4, all within the briefing |
| Plant-floor steps carried out | 0; 2 held for the Head of OT Security |

What the agents did that fixed rules did not: the planner priced combinations of steps on its own, said of one option that it "is paying for a stop and gaining nothing", and added two safety calls, to the Line B shift lead and to the maintenance crew on Line C. The challenger re-priced every option itself before agreeing, and named unknowns the planner had missed, among them that two alarms set aside as unrelated could concern the Line C panel. The recommendation is the same as that of the rule-based first version: EUR 120,000.

What this run does not show, and what was wrong with it:

- The challenger agreed, so the planner never had to answer an objection. The scripted night is an easy one. The harder night has not been run with a model.
- The page is too long for three in the morning. The first-response agent wrote about 450 words and listed plant-floor options, which is not its job. Fixed on 19 November: a word limit per field enforced by the harness, and a narrower role text; in the runs of that day it wrote 52 to 59 words and listed no plant-floor option.
- The agents wrote figures without separators ("EUR 2160000"). Fixed on 19 November in the role texts; the pages of that day show "EUR 2,160,000".
- No hand-in was refused, so the correction path is still shown on prepared replies only.

## The controls around the agents

Fixed code, tested, and not open to persuasion by a model:

- **Every step goes through the Control Tower** under the agent's own identity, and is recorded. Since 20 November 2026 these steps reach the Control Tower through one hook shaped like the tool-call request of the open OWASP Agent Control Standard (allow, deny, ask), in the harness shared by every solution; the standard's wire format and conformance test are designed. The planner can read and price; it cannot disconnect anything. The first-response agent can act on the office side; it has no permission on the plant floor. The challenger can read and price; it can change nothing.
- **No invented figures.** Every euro figure an agent writes must be one the pricing tool produced that night. Any other figure, and the harness hands the result back to be corrected. The decision page takes its figures from the pricing tool, never from an agent's text.
- **No hidden gaps.** A plan that leaves a line within the intruder's reach is accepted only if it says so.
- **Office-side steps are narrow.** Only the steps the briefing allows, only on the office side, only against a device or account that is part of the incident. Each can be undone and says how.
- **Only the named person decides.** The Head of OT Security chooses a response by its number. Any other role is refused and the attempt is recorded. The choice is recorded with its price, whether it was the recommended one, and what the challenger said.
- **No false safety from a missing tool.** When a monitoring tool sends nothing, the page says so at the top, and every line it would have watched is marked "not watched" for every response that does not disconnect it. Without this rule, on the night with the plant-floor monitoring down, closing the office link would cost nothing and look as if it closed every path; the intruder is in fact already on Line B.
- **No out-of-date prices.** When a new alarm arrives, every earlier price is set aside, and a plan that offers a response priced before the alarm is handed back.
- **Short texts.** Every text an agent hands in has a word limit set in the briefing; a longer one is handed back to be shortened.
- **Memory under control.** Cases are written by fixed code and read through the Control Tower; the first-response agent cannot read them and no agent can write them. A change an agent proposes to the briefing is recorded and shown, never applied.
- **A failed agent is visible.** If the planner does not deliver, the page says so and shows what the pricing tool alone knows. If the challenger does not deliver, the page says the recommendation was not challenged.

## What the rule-based first version shows

Measured on 17 November 2026 by running `python -m sentinel run` in this folder. All data is synthetic. Every euro figure is calculated from stated assumptions; none is a measured loss.

The night described above, priced at 03:02:

| Response | Lost production | Lines still within the intruder's reach |
|---|---|---|
| Do nothing and keep watching | EUR 0 | Line A, Line B, Line C |
| Disconnect Line B, cell 2 | EUR 120,000 | Line A, Line B, Line C |
| Close the link between office side and plant floor | EUR 0 | Line B, Line C |
| Disconnect the whole plant floor | EUR 285,500 | none |
| **Disconnect Line B, cell 2 and close the link** | **EUR 120,000** | **none** |

"Everything off" costs EUR 285,500. A targeted response shuts the intruder out just as well for EUR 120,000. At 03:02 nobody in the room had either figure.

| Measure | Result |
|---|---|
| Alarms read from two simulated tools with different formats | 13 |
| Joined into one incident by the fixed rule | 8 |
| Set aside as unrelated, and listed | 5 |
| Responses priced | 5 |
| Decisions by the Control Tower in one run | 13: 11 allowed, 2 held for the Head of OT Security |
| Isolation carried out without a human release | 0 |
| Tests of the first version | 25 of 25 pass |

The full page as generated: [reports/incident-latest.md](reports/incident-latest.md).

## Run it

Python 3.10 or later, nothing to install. From this folder:

```
python -m pytest -q
python -m sentinel run
python -m sentinel waiting
python -m sentinel release --as "Head of OT Security"
```

These need no model and no key. `run` is the rule-based first version; `release` acts on a simulated network: it records that the isolation ran and touches nothing. The tests are 92: 25 for the first version, 15 for the model connector, 36 for the loop, the agents, the page and the decision, 16 for the blind spot, the new alarm, the case memory and the word limits.

The agents need a model. The solution is model-agnostic; the connector provided is for Claude. Put the key in a file outside this repository and point to it:

```
SENTINEL_MODEL_KEY_FILE=/path/to/keyfile python -m sentinel night
SENTINEL_MODEL_KEY_FILE=/path/to/keyfile python -m sentinel night no-safe-response
SENTINEL_MODEL_KEY_FILE=/path/to/keyfile python -m sentinel nights --record
python -m sentinel decide 1 --as "Head of OT Security" --note "what the next night should know"
```

`nights` runs the scripted night and then every night in `data/nights/`, one after the other: the harder night, the night with the plant-floor monitoring down, and the night with a new alarm after the first plan. Every night is written to the case memory in `state/cases/` and can read the earlier ones.

This path has run five times against the model service. On Windows, set `PYTHONUTF8=1` first. A run costs tokens on the key's account: the four nights of 19 November used 296,666 in and 25,107 out together.

## What is in this folder

- `../../shared/harness/` the harness shared by every solution since 20 November 2026: the agent loop (80 lines), the model connector, the hook to the Control Tower, the hand-in checks, the case book and the page frame. `sentinel/loop.py` and `sentinel/model.py` now only point to it
- `sentinel/agents.py` the three agents: what each is told, its tools, and what the harness checks
- `sentinel/night.py` one night from the last alarm to the decision page; `sentinel/decision.py` the page and the decision
- `sentinel/cases.py` the case memory of a night, on the shared case book
- `sentinel/` also holds the rule-based first version: four fixed steps and their workflow (about 500 lines)
- `data/briefing.json` the company briefing the agents read (synthetic)
- `data/nights/` other nights, each as a small file of changes to the scripted night
- `data/plant.json` zones, devices, connections and isolation points of the plant (synthetic)
- `data/production.json` lines, schedule and every assumption behind the prices (synthetic)
- `data/events_office.json`, `data/events_plant.json` the alarms of the two simulated tools
- `reports/incident-latest.md` the page of the first version; `reports/decision-page-sample-scripted.md` a sample decision page on prepared replies
- `reports/runs/` recorded runs with a real model, each as the page and the full record
- `tests/` 92 tests
- `BUILD_LOG.md` decisions, alternatives set aside, corrections and estimated tokens per step

## What has to exist before this solution is called working

| | What | State on 19 November 2026, after the recorded runs |
|---|---|---|
| 1 | A company briefing the agents read; changing it changes their behaviour without changing code. | Working for the part the harness enforces (tested on prepared replies). Read by a model in 5 runs; a changed briefing not yet shown with a model. |
| 2 | A planner agent and a challenger agent in a recorded loop of plan, objection and revision, including a night in which no response closes every path and the agents say so. | Working: recorded with a real model on 19 November, including an objection the planner answered and the night with no safe response. |
| 3 | A run with one security tool missing, in which the decision page names the blind spot. | Working: one recorded run (night `plant-monitoring-down`). |
| 4 | A new alarm arriving mid-run, and a visibly changed plan. | Working: one recorded run (night `new-alarm-after-plan`); the plan changed. The alarm arrives between the planner's first plan and the challenge, not inside an agent's turn. |
| 5 | A decision page on which a named person chooses among options and sees the counter-argument; the choice recorded. | Working: five pages from real runs. The choice is tested on prepared replies. |
| 6 | Reversible office-side steps taken by the agents through the Control Tower; every other step held for a person. | Working: five real runs. |
| 7 | A case memory written after a run and read at the next. | Working: written after every run, read by the agents in three. A case with a decision and a note is tested on prepared replies. |
| 8 | A rehearsal: nights invented by a scenario agent from the briefing, and a report of what each would have cost. | Designed. Three nights are written by hand in `data/nights/`. |
| 9 | The time from the last alarm to the decision page, measured and published. | Five figures, from 49.73 to 77.79 seconds (18 and 19 November 2026). |
| 10 | Results published as rates over many runs, with date and model, including the cases that went wrong. | Five runs, each night once, published with date and model. Not yet a rate. |

The solution is model-agnostic: whoever runs it enters their own model and key.

## Limits

- Everything runs on simulated systems and synthetic data for a fictional company.
- Each night has run once with a model. What a model does on one run, it may not do on the next.
- The new alarm reaches the planner only between its plan and the challenge. An alarm that arrives while an agent is working waits until it hands in.
- The office-side steps do not change the prices: a device the intruder already controls on the plant floor is assumed to stay under its control.
- The recommendation is only as good as the briefing: a wrong cost per hour or an undocumented network connection leads to a wrong answer.
- No probability that the intruder spreads or encrypts is estimated. Lost production is the only cost counted.
- A deputy and a time limit for the named person are not built.
- Connection to real security tools, real production systems and real network equipment is designed, not built.

See the one-page [business case](BUSINESS_CASE.md).
