# Roadmap

Status words used in this repository: "Designed", "In build", "Working".

## Done

- Ten solutions designed, each with a description and a one-page business case.
- Fictional company and shared assumptions defined.
- AI Governance Control Tower, version 0, working: agent registry, policy gateway, audit trail, kill switch, daily volume limit, data labels at the source, an approval queue for the accountable owner of each agent and a one-page board report. What works and what is still a design is listed in [the Control Tower page](../solutions/01-ai-governance-control-tower/README.md).
- First red-team campaign run and published, including the attacks that got through. It has been repeated after each fix; one breach is open and published with its designed fix. See [the latest results](../solutions/01-ai-governance-control-tower/reports/redteam-latest.md).
- OT/IT Convergence Sentinel, rule-based first version, working: fixed code reads the alarms of two simulated security tools, prices each response in lost production and asks for the chosen one through the Control Tower, which holds it for the accountable owner. One scripted incident, no AI agent, no language model. See [the solution page](../solutions/02-ot-it-convergence-sentinel/README.md).
- OT/IT Convergence Sentinel with AI agents, working as a blueprint (19 November 2026): a first-response agent, a planner and a challenger run on a real model, on synthetic data, under the Control Tower. Five recorded runs cover the scripted night, a night with no safe response, a night with the plant-floor monitoring down and a night in which a new alarm changes the plan. Each night ran once, so no rate is stated. Not connected to real systems.

## In build, and what comes next

**Done, 20 November 2026: one shared agent harness.** The agent loop, model connector, hand-in checks and case memory of solution 02 are now one harness for every solution ([shared/harness](../shared/harness)). Every tool call reaches the Control Tower through one hook shaped like the tool-call request of the OWASP Agent Control Standard: allow, deny, or ask a named person. Solution 02 passes its 92 tests on it, unchanged; the harness has 15 of its own. Status: shared harness: working; ACS wire format and conformance test: designed. No new run with a model was made: the behaviour did not change.

**Done, 20 November 2026: solution 10, the AI Value Ledger.** Its ledger is working as fixed code: it reads the recorded runs of the other solutions, prices them from a dated price table and grades every benefit claim as measured, calculated or claimed, with totals held apart by grade. The first measured line is the Sentinel's own cost. Its analyst agent, which challenges each claim and writes the page for the Chief AI Officer, is working as a blueprint: three recorded runs on a real model, one per scenario, 55,538 tokens in and 10,899 out together, under a euro. In those first runs the agent found two faults in the ledger it was given, a line priced at zero by rounding and two states of an agent confused with each other; both were corrected and the published runs are the ones made afterwards. See [the solution page](../solutions/10-ai-value-ledger/README.md).

**In build, 23 November 2026: solution 07, the Self-Healing Service Desk.** Working as fixed code, with no model involved: 200 synthetic tickets, a stand-in for the service desk suite behind one connector, the autonomy ladder that says which ticket types may be worked at which level, the case memory and the page for the Head of IT Service Management. In build: the resolution agent and the verifier, which holds no tool that changes a ticket, on the shared harness, tested on prepared replies in three scenarios. Working as fixed code since 23 November: a red-team campaign of 16 attacks through the ticket, with the agent assumed to be fully taken over: 12 blocked, 1 held for a person, 3 breaches published with the fix designed for each. Recorded on 23 November: 19 agent runs on a real model in three scenarios; the verifier found a flaw in the test data that nobody had planted, the data was corrected and that scenario run again. Next: the red team's live run. Designed: the solution's line in the value ledger. See [the solution page](../solutions/07-self-healing-service-desk/README.md).

**Next: solutions 03, 04, 05, 06, 08 and 09 on the same harness**, so none has to be reworked later, and the value ledger reading its own review runs.

**Designed, for the finish:** the ACS wire format and signature on the hook, then the ACS conformance test run against the gateway, with its result published, including what fails.

**The OT/IT Convergence Sentinel** is working as a blueprint. What is still designed for it, in order:

1. The same nights run several times, so that results can be stated as rates, and a changed briefing run once to show that it changes behaviour.
2. Rehearsals: nights invented by a scenario agent from the briefing.
3. A connector for a second model provider.

The full list is on [the solution page](../solutions/02-ot-it-convergence-sentinel/README.md) under "What has to exist before this solution is called working".

**The AI Governance Control Tower**, paused at version 0 while the first business solution is built. Next for it, in order:

1. Turn the approval queue into a screen with company sign-in, and reduce the load on a single approver.
2. Close the open breach: a second check of outgoing text for personal data that exact comparison cannot see.
3. Run the campaign every night and keep the history.
4. Replace the scripted campaign with a red-team agent driven by a language model.
5. Grow the rule set. Give the board report a quarterly schedule and trends over time.
6. Connect the first real tool, with the gateway as the only holder of its credentials.

## Next steps after that

1. Build the synthetic data generator for the fictional company. Today the synthetic data is a small set of files written for the Control Tower; there is no generator.
2. Connect the Control Tower and the Sentinel to the AI Value Ledger and publish the first board dashboard.
3. Add the remaining solutions one at a time, each as a thin working slice.

## Principles for the build

- One working slice per solution before any polish.
- No agent runs unregistered.
- Every claim in a business case is either measured in this repository or marked as an assumption.
- After each fix, a new attack is written against its edge and published if it gets through.
