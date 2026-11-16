# Roadmap

Status words used in this repository: "Designed", "In build", "Working".

## Done

- Ten solutions designed, each with a description and a one-page business case.
- Fictional company and shared assumptions defined.
- AI Governance Control Tower, version 0, working: agent registry, policy gateway, audit trail, kill switch, daily volume limit, data labels at the source, an approval queue for the accountable owner of each agent and a one-page board report. What works and what is still a design is listed in [the Control Tower page](../solutions/01-ai-governance-control-tower/README.md).
- First red-team campaign run and published, including the attacks that got through. It has been repeated after each fix; one breach is open and published with its designed fix. See [the latest results](../solutions/01-ai-governance-control-tower/reports/redteam-latest.md).

## In build

The AI Governance Control Tower. Next for it, in order:

1. Turn the approval queue into a screen with company sign-in, and reduce the load on a single approver.
2. Close the open breach: a second check of outgoing text for personal data that exact comparison cannot see.
3. Run the campaign every night and keep the history.
4. Replace the scripted campaign with a red-team agent driven by a language model.
5. Grow the rule set. Give the board report a quarterly schedule and trends over time.
6. Connect the first real tool, with the gateway as the only holder of its credentials.

## Next steps after that

1. Build the synthetic data generator for the fictional company. Today the synthetic data is a small set of files written for the Control Tower; there is no generator.
2. Build the first business solution on top of the Control Tower and register its agents.
3. Connect both to the AI Value Ledger and publish the first board dashboard.
4. Add the remaining solutions one at a time, each as a thin working slice.

## Principles for the build

- One working slice per solution before any polish.
- No agent runs unregistered.
- Every claim in a business case is either measured in this repository or marked as an assumption.
- After each fix, a new attack is written against its edge and published if it gets through.
