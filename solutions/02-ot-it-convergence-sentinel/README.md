# OT/IT Convergence Sentinel

**Status: In build. Three agents are built and tested on prepared replies, and there is one recorded run with a real model (18 November 2026). One run shows that the path works; it is not a result on how well the agents reason, and the debate between planner and challenger is not yet shown with a model.** What exists and is tested: the loop the agents work in, the company briefing they read, the controls around them, the decision page, and the rule-based first version whose pricing and plant model are now the agents' tools.

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

| Layer | What it does | Whose job |
|---|---|---|
| Plant-floor monitoring | Knows the machines and controllers; raises alarms on the plant network | Your existing tools |
| Office security | Watches computers, accounts and email | Your existing tools |
| Investigation across both | Joins the alarms and traces the intruder's path, often with AI agents | Your existing tools |
| Network separation | Carries out a disconnection | Your existing tools |
| **The decision** | What each response costs in lost production, which one to take, who decides, and the record of it | **This solution** |

The solution takes the findings of those tools as its input. It does not replace them and does not try to detect better than they do.

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

Stated on 18 November 2026. "Tested on prepared replies" means: the code around the model is tested with a stand-in that replays replies written by hand. That proves the loop and the controls. It does not prove that a model reasons well; only recorded real runs can. One exists so far; it is described in the next section.

| Building block | Status | Model involved |
|---|---|---|
| Model of one plant and its production plan (synthetic files) | Working | No |
| Price of a response in lost production, from the plan | Working, fixed code; now a tool the agents call | No |
| Hold of every plant-floor step for the Head of OT Security, through the Control Tower | Working, fixed code | No |
| Joining the alarms of two simulated tools into one incident | Working as a basic fixed rule | No |
| Agent loop: the model asks for tools, a failed or refused step is handed back to it, and it is finished only when the harness accepts its result | In build: tested on prepared replies; one real run, in which nothing had to be handed back | Yes, once |
| Model connector: one neutral format, a connector for Claude | In build: tested without network; worked in one real run | Yes, once |
| Company briefing that the agents read | In build: tested on prepared replies; read by a model in one run. Not yet shown: a changed briefing changing a model's behaviour | Yes, once |
| First-response agent: reversible office-side steps on its own | In build: tested on prepared replies; one real run | Yes, once |
| Planner agent and challenger agent, with objection and answer | In build: tested on prepared replies; one real run, in which the challenger agreed. Objection and answer not yet shown with a model | Yes, once |
| A night on which no response closes every path | In build: tested on prepared replies | Not yet run |
| Decision page with options, prices and counter-argument; the named person's choice recorded | In build: tested on prepared replies; one page from a real run. The choice was not made in that run | Yes, once |
| Blind spots on the page when a security tool is missing | Designed | |
| A new alarm arriving mid-run | Designed | |
| Case memory and review agent | Designed | |
| Rehearsal: a scenario agent that invents nights from the briefing | Designed | |

A sample of the decision page, produced on prepared replies and labelled as such: [reports/decision-page-sample-scripted.md](reports/decision-page-sample-scripted.md).

In this project the word agent is reserved for a language model working in a loop with tools, checking and correcting its own result. Three such agents are in build here: first response, planner, challenger. The joining of alarms and the writing of the page are fixed code; they hold registry cards in the Control Tower because they act through its gateway, and the registry says of each card what stands behind it.

## The first run with a real model

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
- The page is too long for three in the morning. The first-response agent wrote about 450 words and listed plant-floor options, which is not its job. A word limit enforced by the harness is designed, not built.
- The agents wrote figures without separators ("EUR 2160000"). The figures are priced ones; the format is to be fixed.
- No hand-in was refused, so the correction path is still shown on prepared replies only.

## The controls around the agents

Fixed code, tested, and not open to persuasion by a model:

- **Every step goes through the Control Tower** under the agent's own identity, and is recorded. The planner can read and price; it cannot disconnect anything. The first-response agent can act on the office side; it has no permission on the plant floor. The challenger can read and price; it can change nothing.
- **No invented figures.** Every euro figure an agent writes must be one the pricing tool produced that night. Any other figure, and the harness hands the result back to be corrected. The decision page takes its figures from the pricing tool, never from an agent's text.
- **No hidden gaps.** A plan that leaves a line within the intruder's reach is accepted only if it says so.
- **Office-side steps are narrow.** Only the steps the briefing allows, only on the office side, only against a device or account that is part of the incident. Each can be undone and says how.
- **Only the named person decides.** The Head of OT Security chooses a response by its number. Any other role is refused and the attempt is recorded. The choice is recorded with its price, whether it was the recommended one, and what the challenger said.
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

These need no model and no key. `run` is the rule-based first version; `release` acts on a simulated network: it records that the isolation ran and touches nothing. The tests are 76: 25 for the first version, 15 for the model connector, 36 for the loop, the agents, the page and the decision.

The agents need a model. The solution is model-agnostic; the connector provided is for Claude. Put the key in a file outside this repository and point to it:

```
SENTINEL_MODEL_KEY_FILE=/path/to/keyfile python -m sentinel night
SENTINEL_MODEL_KEY_FILE=/path/to/keyfile python -m sentinel night no-safe-response
python -m sentinel decide 1 --as "Head of OT Security"
```

This path has run once against the model service (see "The first run with a real model"). On Windows, set `PYTHONUTF8=1` first. A run costs tokens on the key's account: the recorded run used 35,342 in and 6,905 out.

## What is in this folder

- `sentinel/loop.py` the agent loop (80 lines)
- `sentinel/agents.py` the three agents: what each is told, its tools, and what the harness checks
- `sentinel/night.py` one night from the last alarm to the decision page; `sentinel/decision.py` the page and the decision
- `sentinel/model.py` the model connector
- `sentinel/` also holds the rule-based first version: four fixed steps and their workflow (about 500 lines)
- `data/briefing.json` the company briefing the agents read (synthetic)
- `data/nights/` other nights, each as a small file of changes to the scripted night
- `data/plant.json` zones, devices, connections and isolation points of the plant (synthetic)
- `data/production.json` lines, schedule and every assumption behind the prices (synthetic)
- `data/events_office.json`, `data/events_plant.json` the alarms of the two simulated tools
- `reports/incident-latest.md` the page of the first version; `reports/decision-page-sample-scripted.md` a sample decision page on prepared replies
- `reports/runs/` recorded runs with a real model, each as the page and the full record
- `tests/` 76 tests
- `BUILD_LOG.md` decisions, alternatives set aside, corrections and estimated tokens per step

## What has to exist before this solution is called working

| | What | State on 18 November 2026 |
|---|---|---|
| 1 | A company briefing the agents read; changing it changes their behaviour without changing code. | Built. Tested on prepared replies for the part the harness enforces. Read by a model in one run; a changed briefing not yet shown with a model. |
| 2 | A planner agent and a challenger agent in a recorded loop of plan, objection and revision, including a night in which no response closes every path and the agents say so. | Built, tested on prepared replies. One recorded real run, in which the challenger agreed; objection, revision and the harder night not yet run with a model. |
| 3 | A run with one security tool missing, in which the decision page names the blind spot. | Not built. |
| 4 | A new alarm arriving mid-run, and a visibly changed plan. | Not built. |
| 5 | A decision page on which a named person chooses among options and sees the counter-argument; the choice recorded. | Built, tested on prepared replies. One page from a real run. |
| 6 | Reversible office-side steps taken by the agents through the Control Tower; every other step held for a person. | Built, tested on prepared replies. Shown in one real run. |
| 7 | A case memory written after a run and read at the next. | Not built. |
| 8 | A rehearsal: nights invented by a scenario agent from the briefing, and a report of what each would have cost. | Not built. |
| 9 | The time from the last alarm to the decision page, measured and published. | One figure: 71.62 seconds, one run, 18 November 2026. |
| 10 | Results published as rates over many runs, with date and model, including the cases that went wrong. | One run so far. A rate needs more. |

The solution is model-agnostic: whoever runs it enters their own model and key.

## Limits

- Everything runs on simulated systems and synthetic data for a fictional company.
- The instructions given to the three agents have been read by a model in one run. That run showed they need tightening (length, format, the first-response agent staying within its job).
- The office-side steps do not change the prices: a device the intruder already controls on the plant floor is assumed to stay under its control.
- The recommendation is only as good as the briefing: a wrong cost per hour or an undocumented network connection leads to a wrong answer.
- No probability that the intruder spreads or encrypts is estimated. Lost production is the only cost counted.
- A deputy and a time limit for the named person are not built.
- Connection to real security tools, real production systems and real network equipment is designed, not built.

See the one-page [business case](BUSINESS_CASE.md).
