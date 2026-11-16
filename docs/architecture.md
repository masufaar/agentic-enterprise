# Shared architecture

The ten solutions share a small set of building blocks. Building them once is what makes each further solution fast to add.

## Shared building blocks

- **Agent registry.** One card per agent: owner, purpose, model, tools, data access, autonomy level.
- **Policy gateway.** Deterministic allow, deny or require-approval decisions on every tool call. The plan is to build on an existing open-source enforcement layer and not to write one from scratch.
- **Human approval workflow.** High-impact actions wait for a named person.
- **Audit trail.** Hash-chained, replayable record of every agent decision.
- **Model-agnostic routing.** Each agent states the model class it needs (small, mid, top). The same agent can run on a hosted model at headquarters or on a self-hosted open model in an isolated plant.
- **Open protocols.** Tools are exposed through the Model Context Protocol; agents talk to each other through an open agent-to-agent protocol.
- **Synthetic data generator.** One generator produces the fictional company's data for all solutions.
- **Evaluation harness.** Every agent has test cases, and results are published in the repository.
- **Cost and benefit schema.** Every agent reports to the AI Value Ledger in one format.

## Additional features planned across the platform

- A live demo that a visitor can click through without installing anything.
- A red-team scoreboard showing how each agent withstood the nightly attacks.
- A comparison of model tiers per agent: quality against cost.
- A one-page board dashboard combining risk (Control Tower) and return (Value Ledger).
