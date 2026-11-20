# agentic-enterprise

A blueprint for company-wide AI transformation in a manufacturer: ten multi-agent solutions for IT and the business, run on one fictional company and governed by one control layer.

**Status: the OT/IT Convergence Sentinel is working as a blueprint: three AI agents run on a real model, on synthetic data, with five recorded runs (18 and 19 November 2026), under the AI Governance Control Tower, which is in build with a working version 0. The AI Value Ledger reads those runs: its ledger is working as fixed code and its analyst agent is in build. Nothing is connected to real systems. The other seven solutions are designs.** Each one moves from "Designed" to "In build" to "Working" in this table as the work progresses. All figures in the business cases are illustrative assumptions for a fictional company.

## Why this repository exists

Most companies run AI as a set of unconnected experiments. A board needs something different: a programme in which every agent has an owner, a business case and a set of rules it cannot break. This repository shows what that programme looks like for a manufacturer with 5,000 employees and plants worldwide.

Background articles:

- [Who approved that AI agent?](https://www.linkedin.com/pulse/who-approved-ai-agent-mario-gracia-rohrf/) on the control layer
- [Who decides to stop the plant?](https://www.linkedin.com/pulse/who-decides-stop-plant-mario-gracia-blhnf/) on the OT/IT Convergence Sentinel
- [Who checks what that AI agent earned?](https://www.linkedin.com/pulse/who-checks-what-ai-agent-earned-mario-gracia-kso3f/) on the AI Value Ledger

## The ten solutions

| # | Solution | Management issue | Business case | Status |
|---|---|---|---|---|
| 1 | [AI Governance Control Tower](solutions/01-ai-governance-control-tower/README.md) | Agents are deployed faster than anyone counts them. When one misbehaves, nobody can say who approved it, what it may touch, or how many others exist. Accountability stays with management and the board. | [Business case](solutions/01-ai-governance-control-tower/BUSINESS_CASE.md) | In build |
| 2 | [OT/IT Convergence Sentinel](solutions/02-ot-it-convergence-sentinel/README.md) | When an attack reaches the plant floor, the security tools say what is happening. Nobody can say what each response costs in lost production, and the decision to disconnect is improvised at night. This solution runs the decision, not the detection, in addition to the existing tools. | [Business case](solutions/02-ot-it-convergence-sentinel/BUSINESS_CASE.md) | Working (blueprint) |
| 3 | [Supply Chain Disruption War Room](solutions/03-supply-chain-disruption-war-room/README.md) | Disruptions are discovered late and the response is improvised over email and spreadsheets. | [Business case](solutions/03-supply-chain-disruption-war-room/BUSINESS_CASE.md) | Designed |
| 4 | [S&OP Negotiation Arena](solutions/04-sop-negotiation-arena/README.md) | Excess inventory ties up working capital while stock-outs still happen, and the monthly planning meeting is driven by positions more than by numbers. | [Business case](solutions/04-sop-negotiation-arena/BUSINESS_CASE.md) | Designed |
| 5 | [Maintenance Closed Loop](solutions/05-maintenance-closed-loop/README.md) | Unplanned downtime, and expertise leaving the company with every retirement. | [Business case](solutions/05-maintenance-closed-loop/BUSINESS_CASE.md) | Designed |
| 6 | [Portfolio Truth Agent](solutions/06-portfolio-truth-agent/README.md) | Executives receive filtered, optimistic reporting and learn about failing projects too late. | [Business case](solutions/06-portfolio-truth-agent/BUSINESS_CASE.md) | Designed |
| 7 | [Self-Healing Service Desk](solutions/07-self-healing-service-desk/README.md) | Slow support, repeated incidents and a high cost per ticket. | [Business case](solutions/07-self-healing-service-desk/BUSINESS_CASE.md) | Designed |
| 8 | [Network Digital Twin](solutions/08-network-digital-twin/README.md) | Outages caused by changes, and slow fault isolation across time zones. | [Business case](solutions/08-network-digital-twin/BUSINESS_CASE.md) | Designed |
| 9 | [Complaint-to-Root-Cause Quality Agent](solutions/09-complaint-to-root-cause-quality-agent/README.md) | Quality investigations take weeks and recalls are scoped too broadly. | [Business case](solutions/09-complaint-to-root-cause-quality-agent/BUSINESS_CASE.md) | Designed |
| 10 | [AI Value Ledger](solutions/10-ai-value-ledger/README.md) | The company spends on AI and cannot say what it gets back. | [Business case](solutions/10-ai-value-ledger/BUSINESS_CASE.md) | In build (ledger working) |

## How the solutions fit together

- **One company.** Every solution runs on the same fictional manufacturer, described in [docs/company-profile.md](docs/company-profile.md).
- **One control layer, owned and open.** Every agent registers with the AI Governance Control Tower before it may act. The Control Tower is the company's own code, designed to follow the open OWASP Agent Control Standard (published 1 September 2026), so agents built with any framework can be checked by the same company rules. Working since 20 November 2026: every tool call of every agent reaches the Control Tower through one hook shaped like the standard's tool-call request (allow, deny, ask), in the [shared agent harness](shared/harness). The standard's wire format, its signature and the conformance test are designed, not yet built: see [the Control Tower page](solutions/01-ai-governance-control-tower/README.md).
- **One ledger.** Every agent reports its cost and benefit to the AI Value Ledger.
- **One architecture.** Shared building blocks are described in [docs/architecture.md](docs/architecture.md).

## Roadmap

See [docs/roadmap.md](docs/roadmap.md).

## Author

Mario Gracia. [LinkedIn profile](https://www.linkedin.com/in/mario-gracia/).
