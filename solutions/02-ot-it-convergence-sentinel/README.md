# OT/IT Convergence Sentinel

**Status: In build. No AI agent runs yet, and no language model is involved so far.** What exists is a tested, rule-based first version of three building blocks the agents will use: the pricing of a response, the model of the plant, and the hold for a named person. The agents described below are designed.

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

| Building block | Status | Model involved |
|---|---|---|
| Model of one plant and its production plan (synthetic files) | Working | No |
| Price of a response in lost production, from the plan | Working, fixed code | No |
| Hold of every isolation for the Head of OT Security, through the Control Tower | Working, fixed code | No |
| Joining the alarms of two simulated tools into one incident | Working as a basic fixed rule | No |
| Company briefing that the agents read | Designed | |
| Planner agent and challenger agent | Designed | Yes |
| Rehearsal: a scenario agent that invents nights from the briefing | Designed | Yes |
| Decision page with options, prices, counter-argument and blind spots | Designed (a simpler generated page exists) | Yes |
| Case memory and review agent | Designed | Yes |
| Reversible office-side steps taken by the agents | Designed | Yes |

The four steps of the first version are registered in the Control Tower as agent cards. They are fixed code. In this project the word agent is reserved for a language model working in a loop with tools, checking and correcting its own result; none exists here yet.

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
| Tests | 25 of 25 pass |

The full page as generated: [reports/incident-latest.md](reports/incident-latest.md).

## Run it

Python 3.10 or later, nothing to install. From this folder:

```
python -m sentinel run
python -m sentinel waiting
python -m sentinel release --as "Head of OT Security"
python -m pytest -q
```

`release` acts on a simulated network: it records that the isolation ran and touches nothing.

## What is in this folder

- `sentinel/` the rule-based first version: four fixed steps, the workflow and the command line (about 500 lines)
- `data/plant.json` zones, devices, connections and isolation points of the plant (synthetic)
- `data/production.json` lines, schedule and every assumption behind the prices (synthetic)
- `data/events_office.json`, `data/events_plant.json` the alarms of the two simulated tools
- `reports/incident-latest.md` the generated page
- `tests/` 25 tests
- `BUILD_LOG.md` decisions, alternatives set aside, corrections and estimated tokens per step

## What has to exist before this solution is called working

1. A company briefing the agents read; changing it changes their behaviour without changing code.
2. A planner agent and a challenger agent in a recorded loop of plan, objection and revision, including a night in which no response closes every path and the agents say so.
3. A run with one security tool missing, in which the decision page names the blind spot.
4. A new alarm arriving mid-run, and a visibly changed plan.
5. A decision page on which a named person chooses among options and sees the counter-argument; the choice recorded.
6. Reversible office-side steps taken by the agents through the Control Tower; every other step held for a person.
7. A case memory written after a run and read at the next.
8. A rehearsal: nights invented by a scenario agent from the briefing, and a report of what each would have cost.
9. The time from the last alarm to the decision page, measured and published.
10. Results published as rates over many runs, with date and model, including the cases that went wrong.

The solution is model-agnostic: whoever runs it enters their own model and key.

## Limits

- Everything runs on simulated systems and synthetic data for a fictional company.
- The recommendation is only as good as the briefing: a wrong cost per hour or an undocumented network connection leads to a wrong answer.
- No probability that the intruder spreads or encrypts is estimated. Lost production is the only cost counted.
- A deputy and a time limit for the named person are not built.
- Connection to real security tools, real production systems and real network equipment is designed, not built.

See the one-page [business case](BUSINESS_CASE.md).
