# AI Governance Control Tower

**Status: Designed. Not built yet.**

The foundation every other agent in this repository plugs into.

## What it is

A registry and control layer for AI agents. Every agent is registered with an owner, a purpose and a list of permitted systems. Every action is checked against company rules before it happens. Every decision is recorded in a tamper-evident trail. A dedicated red-team agent attacks the other agents every night and reports what it found.

## The management issue it solves

Agents are deployed faster than anyone counts them. When one misbehaves, nobody can say who approved it, what it may touch, or how many others exist. Accountability stays with management and the board.

## Why it matters to the business

The board gets one page that answers three questions at any moment: how many agents we run, what each may do, and what happened when one acted. That control is what allows the company to approve new agents in weeks, not months.

## Agents

- Risk classification agent (proposes an EU AI Act risk tier, a human signs off)
- Red-team agent (prompt injection, data exfiltration, privilege escalation)
- Audit reporter (drafts the quarterly AI risk report)

## Data needed

All data is synthetic and belongs to the fictional company described in [docs/company-profile.md](../../docs/company-profile.md).

- Agent inventory (one card per agent in this repository)
- Policy set of 30 to 50 rules (spend limits, data access, plant-floor write restrictions)
- Control catalogue references (EU AI Act, NIST AI RMF, ISO/IEC 42001 control IDs)
- Attack corpus (OWASP agentic risk categories, public prompt-injection sets)

## Additional features planned

- Shadow AI discovery from network and SaaS logs
- Inventory of AI embedded in vendor software (ERP, MES)
- Auto-generated evidence pack for an ISO/IEC 42001 audit

## Next steps

1. Build the registry and the policy gateway on an open-source enforcement layer
2. Register the first two agents from this repository
3. Run the first red-team campaign and publish the results

See the one-page [business case](BUSINESS_CASE.md).
