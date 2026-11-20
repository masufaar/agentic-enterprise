# Shared architecture

The ten solutions share a small set of building blocks. Building them once is what makes each further solution fast to add.

## Shared building blocks

- **Agent registry.** One card per agent: owner, purpose, model, tools, data access, autonomy level.
- **Policy gateway.** Deterministic allow, deny or require-approval decisions on every tool call. It is the project's own small gateway, kept short enough to read in one sitting, and it stays the company's own. It is designed to follow the **OWASP Agent Control Standard (ACS, v0.1.0, published 1 September 2026)**, an open wire specification for exactly this checkpoint: every agent, whatever framework it is built with, sends each tool call to the gateway through the ACS tool-call hooks, and the gateway answers allow, deny or ask (hold for a named person). Status: designed. Not built: the ACS message format and signature, the check of tool results, and a published conformance test run. Details and reasons: [Control Tower page](../solutions/01-ai-governance-control-tower/README.md) and its BUILD_LOG, session 11.
- **Shared agent harness.** One loop, one model connector and one case memory for every solution, taken out of solution 02. Designed; it is the next build.
- **Human approval workflow.** High-impact actions wait for a named person.
- **Audit trail.** Hash-chained, replayable record of every agent decision.
- **Model-agnostic routing.** Each agent states the model class it needs (small, mid, top). The same agent can run on a hosted model at headquarters or on a self-hosted open model in an isolated plant.
- **Open protocols.** Designed: tools described in the shape of the Model Context Protocol (specification 2026-07-28); agents that need to talk to each other use Agent2Agent (A2A v1.0); the record uses the OpenTelemetry generative-AI names (still in Development status upstream); each control is mapped to the OWASP Top 10 for Agentic Applications (2026). The Microsoft Agent Governance Toolkit is designed as an optional adapter, not a dependency.
- **Synthetic data generator.** One generator produces the fictional company's data for all solutions.
- **Evaluation harness.** Every agent has test cases, and results are published in the repository.
- **Cost and benefit schema.** Every agent reports to the AI Value Ledger in one format.

## Additional features planned across the platform

- A live demo that a visitor can click through without installing anything.
- A red-team scoreboard showing how each agent withstood the nightly attacks.
- A comparison of model tiers per agent: quality against cost.
- A one-page board dashboard combining risk (Control Tower) and return (Value Ledger).
