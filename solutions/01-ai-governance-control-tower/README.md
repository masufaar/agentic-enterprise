# AI Governance Control Tower

**Status: In build.** Version 0 is working and tested. It is the simplest possible form of each feature; the table below says exactly what works and what is still a design.

The foundation every other agent in this repository plugs into.

## What it is

A registry and control layer for AI agents. Every agent is registered with an owner, a purpose and a list of permitted systems. Every action is checked against company rules before it happens. Every decision is recorded in a tamper-evident trail. A red-team campaign attacks the agents and the results are published, including the attacks that got through.

## The management issue it solves

Agents are deployed faster than anyone counts them. When one misbehaves, nobody can say who approved it, what it may touch, or how many others exist. Accountability stays with management and the board.

## Why it matters to the business

The board gets one page that answers three questions at any moment: how many agents we run, what each may do, and what happened when one acted. That control is what allows the company to approve new agents in weeks, not months.

## What works today, and what does not

| Feature | Status | What it does in version 0 |
|---|---|---|
| Agent registry | Working | 16 agents from the ten solutions, each with an accountable owner, a named approver, an autonomy level and a permission list. See the [agent inventory](reports/agent-inventory.md). |
| Risk classification | Working (rule-based) | Proposes an EU AI Act tier and the ISO/IEC 42001 control areas for each agent. A proposal for human sign-off, not legal advice. |
| Policy as code | Working | 9 company rules in [data/policies.json](data/policies.json). Design target: 30 to 50. |
| Policy gateway | Working | Allows, denies or holds every action for a named human approver. Fails closed. An agent cannot approve itself. |
| Audit trail | Working | Every decision is recorded. Each record is chained to the one before it, so any later change is detected. |
| Kill switch | Working | Stops one agent or all agents with one command. |
| Red-team campaign | Working (scripted) | 17 attacks and 4 legitimate control actions. See the [latest results](reports/redteam-latest.md). |
| Red-team agent driven by a language model | Designed | Version 0 replays a fixed list of attacks. It does not yet invent new ones. |
| Nightly schedule | Designed | The campaign runs on demand today. |
| Enforcement in front of real tools | Designed | Version 0 decides on what the agent declares. This is the cause of one of the breaches below. |
| Board dashboard, approval workflow screen | Designed | |

## Measured results of the first red-team campaign

Measured on 16 November 2026 by running the campaign in this folder. All data is synthetic.

- 17 attacks: 10 blocked outright, 4 held for a named human approver, **3 got through**.
- 4 of 4 legitimate actions were still allowed, so the result is not achieved by blocking everything.
- The three breaches are published with the fix designed for each in the [results](reports/redteam-latest.md). In short: the gateway believes what an agent says about its own request, it does not follow where data ends up, and it does not count volume over time.

Scope, stated plainly: the campaign assumes the attacked agent is already fully compromised and tests whether the control layer contains it. It does not yet test live language models.

## Try it

Needs Python 3.11 or later. Nothing to install. Run from this folder.

```
python -m control_tower inventory
python -m control_tower check sd-triage ticket.read
python -m control_tower check sourcing-options erp.po.create amount_eur=250000
python -m control_tower kill sd-triage
python -m control_tower redteam
python -m control_tower verify
python -m pytest -q
```

## How it is put together

Plain Python, standard library only, about 480 lines. No database, no server, no language model.

- `data/agents.json` the registry (synthetic)
- `data/policies.json` the company rules
- `data/attacks.json` the red-team campaign
- `control_tower/gateway.py` the single checkpoint every action passes
- `control_tower/audit.py`, `killswitch.py`, `classifier.py`, `registry.py`, `redteam.py`
- `reports/` published results
- [BUILD_LOG.md](BUILD_LOG.md) what was decided, why, and what it cost

The earlier plan was to build on an existing open-source enforcement layer. Version 0 deliberately does not, to keep the first slice small enough to read in one sitting. The gateway has one entry point, so it can be replaced by such a layer later without changing the agents.

## Data

All data is synthetic and belongs to the fictional company described in [docs/company-profile.md](../../docs/company-profile.md). People are named by role only.

## Next steps

1. Close breach A-08: put the gateway in front of the real tool call.
2. Close breaches A-09 and A-10: data labels at the source, volume limits per agent.
3. Run the campaign every night and keep the history.
4. Replace the scripted campaign with a model-driven red-team agent.
5. Grow the rule set towards 30 to 50 rules and add the board one-pager.

See the one-page [business case](BUSINESS_CASE.md).
