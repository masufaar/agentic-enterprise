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
| Gateway carries out the action itself | Working (simulated tools) | The agent hands over the call; the gateway reads the facts from the call, decides, and only then carries it out. For email it reads the real recipients, including copies and blind copies. The tools behind it are simulated: nothing is really sent. |
| Audit trail | Working | Every decision is recorded. Each record is chained to the one before it, so any later change is detected. |
| Kill switch | Working | Stops one agent or all agents with one command. |
| Red-team campaign | Working (scripted) | 20 attacks and 4 legitimate control actions. See the [latest results](reports/redteam-latest.md). |
| Red-team agent driven by a language model | Designed | Version 0 replays a fixed list of attacks. It does not yet invent new ones. |
| Nightly schedule | Designed | The campaign runs on demand today. |
| Connection to real systems | Designed | The gateway must be the only holder of the passwords and keys to the real systems, so that no agent can go around it. Not built: there are no real systems behind it yet. |
| Board dashboard, approval workflow screen | Designed | |

## Measured results of the red-team campaign

Measured on 16 November 2026 by running the campaign in this folder. All data is synthetic.

| | First run | Second run, after the first fix |
|---|---|---|
| Attacks | 17 | 20 |
| Blocked outright | 10 | 10 |
| Held for a named human approver | 4 | 8 |
| **Got through** | **3** | **2** |
| Legitimate actions still allowed | 4 of 4 | 4 of 4 |

- The first run found that an agent could lie about where an email was going. That is closed: the gateway now reads the recipients from the email itself. Three new attacks on the fix (hidden blind copy, look-alike domain, malformed address) were added and are all held.
- Two breaches remain open and are published with the fix designed for each in the [results](reports/redteam-latest.md): the gateway does not follow where data ends up, and it does not count volume over time.

Scope, stated plainly: the campaign assumes the attacked agent is already fully compromised and tests whether the control layer contains it. It does not yet test live language models, and the tools behind the gateway are simulated.

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

Plain Python, standard library only, about 550 lines. No database, no server, no language model.

- `data/agents.json` the registry (synthetic)
- `data/policies.json` the company rules
- `data/attacks.json` the red-team campaign
- `control_tower/gateway.py` the single checkpoint every action passes
- `control_tower/tools.py` reads the facts from each call; simulated tools
- `control_tower/audit.py`, `killswitch.py`, `classifier.py`, `registry.py`, `redteam.py`
- `reports/` published results
- [BUILD_LOG.md](BUILD_LOG.md) what was decided, why, and what it cost

The earlier plan was to build on an existing open-source enforcement layer. Version 0 deliberately does not, to keep the first slice small enough to read in one sitting. The gateway is one small component, so it can be replaced by such a layer later without changing the agents.

## Data

All data is synthetic and belongs to the fictional company described in [docs/company-profile.md](../../docs/company-profile.md). People are named by role only.

## Next steps

1. Close breaches A-09 and A-10: data labels at the source, volume limits per agent.
2. Run the campaign every night and keep the history.
3. Replace the scripted campaign with a model-driven red-team agent.
4. Grow the rule set towards 30 to 50 rules and add the board one-pager.
5. Connect the first real tool, with the gateway as the only holder of its credentials.

See the one-page [business case](BUSINESS_CASE.md).
