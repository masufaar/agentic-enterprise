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
- Published: M gave his go on 16 November 2026 and version 0 was pushed to the public repository (commit 2324cb9). A working copy of all files is kept in the Desktop folder agentic-enterprise.

## Session 2, 16 November 2026

Goal: close breach A-08, where an agent could state that an email was internal while the real address was external.

### What was wrong

The gateway decided on a description of the action written by the agent. A compromised agent simply described it falsely. The rule itself (P-006) was correct; it was being fed the agent's word.

### Decisions

| # | Decision | Why | Alternative set aside |
|---|---|---|---|
| D10 | The gateway carries out the action itself (`Gateway.execute`). The agent hands over the call and never touches the tool. | Whoever checks must also be the one who acts, otherwise the checked thing and the done thing can differ. This is the smallest change that makes that true. | Asking agents to describe actions honestly, or checking descriptions harder. Neither helps against a compromised agent. |
| D11 | The gateway works out the facts its rules need from the call itself and overwrites whatever the agent claimed. | Removes the agent's word from the decision. One small function per tool (`tools.py`); today only email needs one. | Trusting some fields and not others, case by case. |
| D12 | All recipient fields count (to, copy, blind copy). One outside or unreadable address makes the whole email "outside". | The obvious next attack after the fix is to hide the outside address. | Looking at the main recipient only. |
| D13 | An address the gateway cannot read with certainty is treated as outside. | Same fail-closed principle as D7. While testing I found my own first idea (take the text after the last @) could be fooled by an address containing two @ signs, so the check accepts only a strictly well-formed address. | Best-effort parsing. |
| D14 | Tools stay simulated. | There are no real systems yet. The README says so. The remaining exposure, an agent reaching a real system around the gateway, is a matter of who holds the credentials and is listed as "Designed". | Wiring a real mail server now. |
| D15 | Kept `check()` as a dry run for people. | Useful to ask "would this be allowed?" without doing anything. Agents use `execute()`. | Removing it. |
| D16 | No delegation to a lighter model this session. | The work was about 70 lines of security-sensitive logic and its tests. Session 1 measured about 76,000 tokens of overhead for one delegated file; that is not worth it for a task this small, and this is the kind of code I should not hand down. | Delegating the tests. |

### Steps and cost

| Step | What | Model | Tokens |
|---|---|---|---|
| 1 | `tools.py`: fact reader for email, simulated tools | Main (Fable 5.2) | About 500 estimated output |
| 2 | `Gateway.execute` | Main | About 250 estimated output |
| 3 | Three new attacks (A-18, A-19, A-20), ten new tests | Main | About 900 estimated output |
| 4 | Ran tests and campaign. One slip of mine: a self-check in my edit script had the wrong expected count and stopped the edit halfway; I re-applied the remaining edits. No code defect. | Main | Small |
| 5 | README, this log | Main | About 1,700 estimated output |

Same caveat as before: estimates cover text written, not reading and reasoning.

### Measured results

- 22 of 22 tests pass (12 before).
- Campaign: 20 attacks, 10 blocked, 8 held for a human, 2 breaches (A-09, A-10). 4 of 4 legitimate actions allowed. A-08 is now held.
- Audit trail: 83 records after one campaign, chain intact.
- Size: about 550 lines of Python.

### Open points

- The fix is proven against simulated tools only.
- "Held for a human" is only as good as the human. Eight of twenty attacks now end on an approver's desk; approval fatigue is a real risk and the approval screen is not built.
- Unchanged from session 1: legal references unverified; thresholds are assumptions.
- Published: M gave his go on 16 November 2026 and this session's changes were pushed to the public repository.
