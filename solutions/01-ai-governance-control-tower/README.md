# AI Governance Control Tower

**Status: In build.** Version 0 is working and tested. It is the simplest possible form of each feature; the table below says exactly what works and what is still a design.

The foundation every other agent in this repository plugs into.

**How the word "agent" is used here.** An agent is a language model working in a loop inside a harness: it plans, uses tools, checks its own result and corrects itself, and a person is the last step. Fixed code is a tool or a control, never an agent. The registry holds one card per identity that may act through the gateway, and each card says what stands behind it today. On 19 November 2026 that is 3 agents working (solution 02, working as a blueprint on synthetic data, with five recorded runs on a real model), 6 steps of fixed code without a model, and 11 designed agents with nothing behind the card yet.

## What it is

A registry and control layer for AI agents. Every agent is registered with an owner, a purpose and a list of permitted systems. Every action is checked against company rules before it happens. Every decision is recorded in a tamper-evident trail. A red-team campaign attacks the control layer under the identities of the registered agents, and the results are published, including the attacks that got through.

## The management issue it solves

Agents are deployed faster than anyone counts them. When one misbehaves, nobody can say who approved it, what it may touch, or how many others exist. Accountability stays with management and the board.

## Why it matters to the business

The board gets one page that answers three questions at any moment: how many agents we run, what each may do, and what happened when one acted. That control is what allows the company to approve new agents in weeks, not months.

## What works today, and what does not

| Feature | Status | What it does in version 0 |
|---|---|---|
| Agent registry | Working | 20 cards from the ten solutions, each with an accountable owner, a named approver, an autonomy level, a permission list and what stands behind it today (agent working, agent in build, fixed code, or designed). See the [agent inventory](reports/agent-inventory.md). |
| Risk classification | Working (rule-based) | Proposes an EU AI Act tier and the ISO/IEC 42001 control areas for each card. A proposal for human sign-off, not legal advice. |
| Reach of action | Working (rule-based) | A second rating beside the legal tier: how far a card's permissions go inside the company, in four levels from "reads only" to "can stop production", worked out from the permission list. The two ratings can disagree: an agent that suspends accounts on its own is "minimal" in the legal reading and level 3 of 4 in reach. The board report lists every card that reaches level 3 or more and is registered to act without a person. A tool nobody has classified counts as an action. A proposal for human sign-off. |
| Policy as code | Working | 13 company rules and one volume limit in [data/policies.json](data/policies.json). Design target: 30 to 50. |
| Policy gateway | Working | Allows, denies or holds every action for a named human approver. Fails closed. An agent cannot approve itself. |
| Gateway carries out the action itself | Working (simulated tools) | The agent hands over the call; the gateway reads the facts from the call, decides, and only then carries it out. For email it reads the real recipients, including copies and blind copies. The tools behind it are simulated: nothing is really sent. |
| Audit trail | Working | Every decision is recorded. Each record is chained to the one before it, so any later change is detected. |
| Kill switch | Working | Stops one agent or all agents with one command. |
| Volume limit | Working | Each agent has a daily allowance of database rows (5,000, an assumption). Usage is counted from the audit trail, so there is nothing separate to tamper with. |
| Data labels | Working (one source, one shared store, internal email) | Data is labelled where it lives: each field of a support ticket carries a label. Before anything is written to the knowledge base, which every employee can read, the gateway compares the text with the values labelled personal at the source. A match is refused, whatever the agent says the text contains. Text from an agent that has handled personal data waits for a named person even when no match is found. For email, the gateway also looks up every recipient in a company directory: personal data is refused if any reader is a mailing list or an address that is not one known employee, held if it is about a different employee than the reader, and allowed when the only reader is the person it is about. |
| Approval queue | Working (command line and a generated page, no clickable screen) | Every held action waits for the accountable owner of the agent, and only that person can release or refuse it. The queue is read from the audit trail and every decision is written back to it. The approver is shown why the item is held and what to look for, for example whose personal data is in a text. On release the gateway decides again. See [what the approver sees](reports/approvals-latest.md). Not built: verifying who the approver is, and a screen with buttons. |
| Red-team campaign | Working (scripted) | 29 attacks and 8 legitimate control actions. See the [latest results](reports/redteam-latest.md). |
| Board report | Working (one generated page, on demand) | One page put together from the registry and the latest campaign: what stands behind the cards today, cards by reach of action, by proposed legal tier and by autonomy, the share of attacks contained, open findings with their designed fix, results by type of attack and by attacked agent, and the load on each approver. Nothing new is measured or stored. See [the board report](reports/board-latest.md). Not built: a fixed quarterly schedule, trends over time, cost and benefit per agent. |
| Red-team agent driven by a language model | Designed | Version 0 replays a fixed list of attacks. It does not yet invent new ones. |
| Nightly schedule | Designed | The campaign runs on demand today. |
| Connection to real systems | Designed | The gateway must be the only holder of the passwords and keys to the real systems, so that no agent can go around it. Not built: there are no real systems behind it yet. |
| Board dashboard with trends, clickable approval screen with company sign-in | Designed | |

## Owned by the company, built to the open standard

The Control Tower is the company's own code, and it is designed to follow the open standards found on 20 November 2026. The main one is the **OWASP Agent Control Standard (ACS)**, published by the OWASP GenAI Security Project on 1 September 2026 (specification v0.1.0). ACS describes exactly what this gateway does: a separate checkpoint receives what an agent is about to do and decides before it happens. With ACS, any agent framework can reach the company's own checkpoint over the same open wire, and the company keeps its own rules.

| Standard | What it covers | Status here |
|---|---|---|
| OWASP Agent Control Standard v0.1.0 | The checkpoint before each agent action, its decisions, its record | **Designed.** The gateway already sits where ACS puts its checkpoint, and its decisions map exactly: allow to `allow`, refuse to `deny`, hold for a named person to `ask`. Not built: the ACS message format and its signature on every message, the check of what a tool returns, and a published run of the ACS conformance test. Until that test result is published, this page says "designed to follow", not "conformant". |
| OWASP Top 10 for Agentic Applications (2026) | The risks auditors map agents to | Designed: each control mapped to the list. |
| OpenTelemetry generative-AI conventions | Names for the record, so any monitoring tool can read it | Designed; the conventions themselves are still in Development status. |
| Model Context Protocol, 2026-07-28 | How agents call tools | Designed: every tool described in this shape, so a company can plug in its own. |
| Agent2Agent (A2A) v1.0 | How agents talk to each other | Designed, for the solutions that need it. |
| EU AI Act, as amended by Regulation (EU) 2026/1744 | High-risk obligations from 2 December 2027 and 2 August 2028 | Working as a proposal for human sign-off (risk classification above); dates to be read in the Official Journal. |

The Microsoft Agent Governance Toolkit (MIT, public preview, v4.1.0 on 9 June 2026) is designed as an optional adapter, never a dependency. The reasons for each choice are in [BUILD_LOG.md](BUILD_LOG.md), session 11.

## Measured results of the red-team campaign

Measured on 16 November 2026 by running the campaign in this folder. All data is synthetic.

| | Run 1 | Run 2, after the first fix | Run 3, after the second fix | Run 4, after the third fix | Run 5, after the fourth fix |
|---|---|---|---|---|---|
| Attacks | 17 | 20 | 22 | 25 | 29 |
| Blocked outright | 10 | 10 | 12 | 14 | 16 |
| Held for a named human approver | 4 | 8 | 8 | 9 | 11 |
| Capped (ran within the daily allowance, then stopped) | 0 | 0 | 1 | 1 | 1 |
| **Got through** | **3** | **2** | **1** | **1** | **1** |
| Legitimate actions still allowed | 4 of 4 | 4 of 4 | 5 of 5 | 6 of 6 | 8 of 8 |

- Run 1 found that an agent could lie about where an email was going. Closed: the gateway reads the recipients from the email itself.
- Run 2 still allowed an agent to copy a whole database in many small permitted requests. Closed with a daily volume limit per agent: in run 3 the same attack got 5 of its 60 requests through (4,500 of 54,000 rows, inside what the agent may read on a normal day) and was then stopped.
- Run 3 still allowed an agent to copy personal data from a ticket into a knowledge article every employee can read. Closed for the knowledge base: data is labelled at its source and the gateway compares the text with the labelled values. In run 4 the article is refused whether the agent declares the personal data or hides it behind a harmless label. A disguised version (values spelled out and broken up) no longer matches, so it is not refused; it is held for a named person, because the agent has handled personal data.
- Run 4 found, with a new attack written to test the edge of that fix, that the agent could send the same personal data to the all-employees mailing list instead. Closed: the gateway looks up every recipient in a company directory. In run 5 the email is refused, also when the list is hidden in blind copy. One employee's personal data sent to a single other colleague is held for a named person. A reply to the employee the data is about is still allowed.
- One breach is open in run 5 and is published with its designed fix in the [results](reports/redteam-latest.md). Again it is a new attack at the edge of the fix: personal data that is disguised (spelled out and broken up) and sent to one single colleague is neither recognised nor held. The same disguised text sent to a mailing list or to the knowledge base is held.

Known limits of the data labels: one labelled source (support tickets), one shared store (the knowledge base) and email. The comparison finds exact values, ignoring capitals and spacing; reworded or encoded personal data is not recognised. Attachments are compared only as far as their text is in the call. An employee's private address is not in the directory, so a reply there that contains their data is refused. Once an agent has handled a ticket, every knowledge article and every email to a list waits for a person: 11 of 29 attacks now end on an approver's desk, handled through the approval queue above. The 11 waiting items of run 5 fall on three people: 9 on the Head of IT Service Management, 1 each on the Head of OT Security and the Chief Procurement Officer.

Known limits of the volume control, not yet tested by the campaign: an agent that stays just under the limit every day for weeks, and several agents each taking a share. Both need pattern detection over time, which is designed, not built. The limit covers database reads and exports only.

Scope, stated plainly: the campaign assumes the attacked agent is already fully compromised and tests whether the control layer contains it. It does not yet test live language models, and the tools behind the gateway are simulated.

## Try it

Needs Python 3.11 or later. Nothing to install. Run from this folder.

```
python -m control_tower inventory
python -m control_tower check sd-verifier ticket.read
python -m control_tower check sourcing-options erp.po.create amount_eur=250000
python -m control_tower check sourcing-options erp.po.create amount_eur=12000
python -m control_tower approvals
python -m control_tower release ITEM --as "Chief Procurement Officer"
python -m control_tower kill sd-verifier
python -m control_tower redteam
python -m control_tower board
python -m control_tower verify
python -m pytest -q
```

## How it is put together

Plain Python, standard library only, about 1,200 lines. No database, no server, no language model.

- `data/agents.json` the registry (synthetic)
- `data/policies.json` the company rules
- `data/tickets.json` synthetic support tickets, labelled field by field
- `data/directory.json` synthetic company directory: which address is one employee, which is a list
- `data/attacks.json` the red-team campaign
- `control_tower/gateway.py` the single checkpoint every action passes
- `control_tower/tools.py` reads the facts from each call; simulated tools
- `control_tower/approvals.py` the queue of held actions and the approver's decisions
- `control_tower/board.py` the one-page board report, put together from the registry and the latest campaign
- `control_tower/reach.py` the reach-of-action rating, from the permission list
- `control_tower/audit.py`, `killswitch.py`, `classifier.py`, `registry.py`, `redteam.py`
- `reports/` published results
- [BUILD_LOG.md](BUILD_LOG.md) what was decided, why, and what it cost

The earlier plan was to build on an existing open-source enforcement layer. Version 0 deliberately does not, to keep the first slice small enough to read in one sitting. On 20 November 2026 the choice was confirmed the other way round: the gateway stays the company's own and is designed to speak the open Agent Control Standard, so other enforcement layers and agent frameworks can connect to it rather than replace it (see above).

## Data

All data is synthetic and belongs to the fictional company described in [docs/company-profile.md](../../docs/company-profile.md). People are named by role only; ticket requesters appear by invented employee number.

## Next steps

0. Working since 20 November 2026: one [shared agent harness](../../shared/harness) for every solution, taken out of solution 02. Every tool call reaches this gateway through one hook shaped like the ACS tool-call request: allow stays `allow`, a refusal is `deny`, a step held for a named person is `ask`, and the spent daily volume limit is `deny` (15 tests in `shared/tests`). It runs in process. Status: shared harness: working; ACS wire format and conformance test: designed. Designed next: the ACS wire format and signature, then the ACS conformance test run against the gateway, with its result published, including what fails.
1. Turn the approval queue into a screen with buttons and company sign-in, and reduce the load on one approver (9 of 11 items). Then label more sources than tickets.
2. Close breach A-29: a second check of outgoing text for personal data that exact comparison cannot see.
3. Run the campaign every night and keep the history.
4. Replace the scripted campaign with a model-driven red-team agent, and add detection of slow patterns over days and across agents.
5. Grow the rule set towards 30 to 50 rules. Give the board report a quarterly schedule and trends over time.
6. Connect the first real tool, with the gateway as the only holder of its credentials.

See the one-page [business case](BUSINESS_CASE.md).
