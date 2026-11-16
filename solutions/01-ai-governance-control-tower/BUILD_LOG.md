# Build log: AI Governance Control Tower

A running record of what was done, why, how, and what it cost. Newest session at the bottom.

## How to read the token figures

- **Measured** figures come from the tool that ran the step.
- **Estimated** figures are file size divided by four (a common rule of thumb for English text and code). They cover the text that was written, not the reading and reasoning behind it.
- The main model cannot read its own token meter from inside the session. The session total therefore has to be taken from the usage screen, not from this file.

## Session 1, 16 November 2026

Goal given: build the Control Tower with the simplest architecture, delegate simple tasks to other models, log everything.

### Decisions

| # | Decision | Why | Alternative set aside |
|---|---|---|---|
| D1 | Plain Python, standard library only. No database, server or framework. | Simplest thing that works. Anyone can run it with nothing to install, and a reviewer can read all of it in one sitting. Package installs were also not available in the build environment. | A web service with a database. Adds weeks and proves nothing more at this stage. |
| D2 | Do not build on the open-source enforcement layer yet (the handover named Microsoft's Agent Governance Toolkit). | It could not be installed in this environment, and I have not verified its current interface. The gateway has one entry point (`Gateway.check`) so it can be swapped in later. | Building on it now, unverified. |
| D3 | No language model in version 0. Classification and red-team are rule-based and scripted. | Deterministic results that can be measured and repeated at zero running cost. The README says so openly. | A model-driven red-team agent. Next step, once the gateway sits in front of real tools. |
| D4 | The red-team assumes the attacked agent is already compromised. | It tests the question a board cares about: when the model is fooled, does the control hold? It also needs no model to run. | Testing whether a model can be fooled. Useful later, but model-dependent. |
| D5 | Publish the breaches. Three attacks were written to probe real gaps, and they get through. | A result of 17 out of 17 blocked would not be believed and would not be true of any real control layer. A test fails if a new breach appears or a known one disappears unnoticed. | Only including attacks that are blocked. |
| D6 | Human approval comes from the calling workflow, never from the agent's own request. | Otherwise an agent could write "approved by the CFO" into its request. Attack A-13 tests exactly this. | Reading approval from the request. |
| D7 | Missing or malformed values count as a violation (fail closed). | An attacker's first move is to leave out the field that is checked. Attack A-07. | Skipping the rule when the value is absent. |
| D8 | Hash-chained audit file. | Tamper evidence with no infrastructure. Verified by changing one record and seeing the check fail. | A database with access controls. |
| D9 | People appear by role title only. | Synthetic data rule; avoids any accidental resemblance to real people. | Invented names. |

### Steps and cost

| Step | What | How | Model | Tokens |
|---|---|---|---|---|
| 1 | Read handover, elevator pitch, project instructions | Project docs | Main (Fable 5.2) | Input only, about 4,500 estimated |
| 2 | Cloned the repository, read the existing README and architecture | git, read-only | Main | Input only, about 3,500 estimated |
| 3 | Wrote the synthetic agent inventory, 16 agents (`data/agents.json`) | Delegated with an exact schema and tool vocabulary; I checked the output line by line and by loading it | **Lighter model (Haiku)** | **75,980 measured** (57 seconds). The file itself is about 4,200. |
| 4 | Registry, classifier, audit trail, kill switch | Written directly | Main | About 1,800 estimated output |
| 5 | Policy rules and gateway | Written directly | Main | About 1,900 estimated output |
| 6 | Attack list, red-team runner, command line | Written directly | Main | About 3,500 estimated output |
| 7 | Tests (12) | Written directly | Main | About 1,100 estimated output |
| 8 | Ran tests and the campaign; found and fixed one defect (see below) | Shell | Main | Small |
| 9 | README, this log | Written directly | Main | About 3,000 estimated output |

Observation on delegation: the lighter model produced correct data on the first attempt, but 75,980 tokens for a 4,200-token file is not efficient. Most of that is the fixed overhead of starting a separate agent. Delegation pays for larger batches of simple work (for example the remaining policy rules, or synthetic data for all ten solutions in one go), not for single small files. Whether it was cheaper in money than doing it on the main model depends on the price ratio between the two models, which I have not verified.

### Defect found and fixed

The first test run failed. An empty audit log counted as "nothing" in Python, so the gateway silently fell back to the default log file instead of the one it was given. In production that would mean decisions recorded in the wrong place. Fixed in `gateway.py` by testing explicitly for "not provided". All 12 tests pass after the fix.

### Measured results

- 12 of 12 tests pass.
- Red-team campaign: 17 attacks, 10 blocked, 4 held for a human, 3 breaches. 4 of 4 legitimate actions allowed.
- Audit trail: 80 records after one campaign, chain intact. Changing one record by hand was detected at the right record.
- Size: about 480 lines of Python.

### Open points and things I am unsure about

- The EU AI Act article references and the ISO/IEC 42001 control area names in `classifier.py` are from my own knowledge. I have not checked them against the official texts in this session. They need a check before anyone relies on them.
- Classifying the plant-floor response agent as high risk ("safety component") is a cautious assumption, not a legal finding.
- The thresholds in the rules (EUR 10,000, 1,000 rows) are illustrative assumptions.
- Nothing has been committed or pushed. That waits for M's go.
