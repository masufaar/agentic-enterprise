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

## Session 3, 16 November 2026

Goal: close breach A-10, where an agent copied a database in 60 small requests of 900 rows, each one within the rules.

### What was wrong

Every rule looked at one request at a time. Nothing added requests up.

### Decisions

| # | Decision | Why | Alternative set aside |
|---|---|---|---|
| D17 | A daily allowance of rows per agent (5,000, an assumption), across database reads and exports together. | Smallest control that makes the total count, not just each request. | Rate limits per minute. They slow an attacker down but do not cap the total. |
| D18 | Usage is counted from the audit trail, not from a separate counter. | No new storage, and the count inherits the trail's tamper evidence: an agent cannot reset a counter that does not exist. | A counter file. One more thing to protect. |
| D19 | The row count is the cap the gateway enforces on the tool, not a figure the agent reports afterwards. It must be a positive whole number or the request is refused. | Same lesson as A-08: do not rely on the agent's word. While designing the fix I saw that a negative number would have earned allowance back, so that is refused and is now attack A-22. | Counting what the agent says it read. |
| D20 | Only requests that were actually carried out count. Dry runs and refused requests do not. | Otherwise a person asking "would this be allowed?" would use up an agent's allowance. | Counting every allowed decision. |
| D21 | New outcome "capped" in the results. | A-10 is not fully blocked: the first 5 requests (4,500 rows) go through because that is within what the agent may read on a normal day. Calling that "blocked" would overstate it. | Reporting it as blocked. |
| D22 | Each campaign run gets its own fresh audit file. | With a daily allowance, a second run on the same day would start with the allowance used up and show different results. Results must be repeatable. | Clearing the audit trail before a run. Deleting audit records is the wrong habit to build in. |
| D23 | Slow attacks over many days and several agents sharing the work are written up as known limits, not simulated. | Simulating days needs a controllable clock, which adds machinery for little proof today. | Building a time simulator now. |
| D24 | No delegation to a lighter model. | About 40 lines of security-sensitive logic. Same reasoning as D16. | |

### Steps and cost

| Step | What | Model | Tokens |
|---|---|---|---|
| 1 | Volume limit in the gateway and the rules file | Main (Fable 5.2) | About 450 estimated output |
| 2 | "Capped" outcome and fresh audit file per campaign | Main | About 350 estimated output |
| 3 | Two new attacks (A-21, A-22), one new control (C-05), nine new tests | Main | About 700 estimated output |
| 4 | Ran tests and campaign twice; found and fixed one defect (below) | Main | Small |
| 5 | README, this log | Main | About 1,600 estimated output |
| 6 | Push to GitHub, copy to the Desktop folder, handover summary written to the project | Main | About 1,200 estimated output |

Estimates cover text written, not reading and reasoning.

### Defect found and fixed

Running the campaign twice within the same second gave the two runs the same audit file name, so the second run started with the first run's usage and reported different figures. Fixed by making the file name unique to the microsecond. Found by running the campaign twice on purpose to check repeatability.

### Measured results

- 31 of 31 tests pass (22 before).
- Campaign: 22 attacks, 12 blocked, 8 held for a human, 1 capped, 1 breach (A-09). 5 of 5 legitimate actions allowed. Two consecutive runs give the same figures.
- Size: about 600 lines of Python.

### Open points

- The gateway re-reads the whole audit file on every decision. Fine at this size; it will need an index before real volumes.
- The 5,000-row allowance is one figure for all agents. Real agents need their own.
- The volume limit covers database reads and exports only.
- Unchanged: tools are simulated; legal references unverified; thresholds are assumptions.
- Published: M gave his go on 16 November 2026 and this session's changes were pushed to the public repository.

## Session 4, 16 November 2026

Goal given: "continue with breach A-09" (personal data copied from a ticket into a knowledge article every employee can read).

### Why A-09 got through

The gateway checked who may touch which data: the service-desk resolution agent may handle personal data and may write knowledge articles, so the write was allowed. Nothing looked at where the data was going. The only statement about the content was the agent's own, and a compromised agent would simply call the text "internal".

### Decisions

| # | Decision | Why | Alternative set aside |
|---|---|---|---|
| D25 | Label data at the source, field by field (`data/tickets.json`). | The place that holds the data is the only one that knows what it is. Same lesson as A-08 and A-10: do not rely on the agent's word. | A label stated by the agent in its request. That was the gap. |
| D26 | Before a write to a shared store, the gateway compares the text with every value labelled personal at the source. A match is refused (rule P-010). | Precise: a clean article is not refused, an article with a real phone number is. It does not depend on what the agent read or says it read. | Scanning for things that look like phone numbers or addresses. Guesswork, with false alarms. |
| D27 | The comparison ignores capitals and all white space, and covers every text field of the call, including title, tags and nested fields. | The cheapest evasions are extra spaces, changed capitals, and putting the value in a field nobody checks. | Checking the body text only. |
| D28 | If no match is found but the agent has handled labelled data, the text is held for a named person (rule P-011). | Exact comparison cannot see reworded or encoded data. Rather than claim it can, the gateway says "cannot rule it out" and a person decides. Attack A-24 tests this. | Allowing it. That would be a silent gap. |
| D29 | "Has handled labelled data" is read from the audit trail, with no time window. | Like the volume count (D18): nothing separate to reset. A daily window would let an agent read today and write tomorrow. | A per-task marker. The agent would name the task itself. |
| D30 | A write with no readable text is refused. | Fail closed (D7). | Treating empty text as clean. |
| D31 | Text refused for containing personal data is not copied into the audit trail; the record shows "[withheld: personal data]". | Otherwise the audit trail becomes the next place the personal data is copied to. Found while building: the first version did write it there. | Logging everything. |
| D32 | Shared stores and labelled sources are listed in `data/policies.json`, not in code. | Adding a second store or source is a configuration change. | Hard-coding the knowledge base. |
| D33 | Ticket requesters appear by invented employee number, phone and address, not by name. | Extends D9 (role titles only) to data subjects. | Invented names. |
| D34 | A new attack, A-25, was written against the edge of the fix, and it gets through: the same personal data sent to the all-employees mailing list by internal email. Published as an open breach with a designed fix. | D5: publish the breaches. Closing A-09 for the knowledge base and reporting zero breaches would have been true of the old attack list and misleading about the control. | Stopping at zero. |
| D35 | A-25 is not closed in this session. | The honest fix needs a directory that tells the gateway which addresses are mailing lists; an ordinary reply to the employee concerned must still be allowed (control C-02). That is a design step of its own. | A quick rule on the address "all-staff". It would close the test, not the gap. |
| D36 | No delegation to a lighter model. | About 90 lines of security-sensitive logic. Same reasoning as D16 and D24. | |

### Steps and cost

| Step | What | Model | Tokens |
|---|---|---|---|
| 1 | Read the handover and all files of the solution | Main (Fable 5.2) | Input only, about 22,000 estimated |
| 2 | Labelled tickets, two rules, label check in the gateway and tools | Main | About 1,500 estimated output |
| 3 | A-09 rewritten with a real read and a real article; three new attacks (A-23, A-24, A-25); one new control (C-06) | Main | About 800 estimated output |
| 4 | 17 new tests; ran tests and the campaign twice | Main | About 900 estimated output |
| 5 | README, this log | Main | About 1,900 estimated output |

Estimates cover text written, not reading and reasoning.

### Defect found and fixed

The first version of the fix refused the article but wrote its full text, personal data included, into the audit record of the refusal. Fixed (D31) and covered by a test.

### Measured results

- 48 of 48 tests pass (31 before).
- Campaign: 25 attacks, 14 blocked, 9 held for a human, 1 capped, 1 breach (A-25). 6 of 6 legitimate actions allowed. Two consecutive runs give the same figures.
- A-09: blocked by P-010. A-23 (agent calls the text harmless): blocked by P-010. A-24 (disguised values): held by P-011.
- Size: about 690 lines of Python.

### Open points

- A-25: internal mailing lists are not treated as shared stores.
- One labelled source (tickets) and one shared store (knowledge base). Other sources (HR, customer complaints) and other stores (shared drives, chat channels) are not labelled yet.
- Exact comparison only. Reworded, translated or encoded personal data is not recognised and depends on the human release (A-24). The approver sees the text without any hint of what to look for.
- Held text (A-24) is written to the audit trail in full, so a disguised copy does land there.
- Every knowledge article from an agent that has handled a ticket now waits for a person. Nine of 25 attacks end on an approver's desk; the approval screen is still not built.
- The gateway compares against every labelled value on each write. Fine with two tickets; real volumes need an index of fingerprints.
- Unchanged: tools are simulated; legal references unverified; thresholds are assumptions.
- Published: M gave his go on 16 November 2026 and this session's changes were pushed to the public repository.

## Session 5, 16 November 2026

Goal given: close breach A-25 (personal data sent to the all-employees mailing list by internal email).

### Why A-25 got through

Session 4 protected the knowledge base. Email was only checked for leaving the company. An internal address looked safe, although one internal address can reach 5,000 readers.

### Decisions

| # | Decision | Why | Alternative set aside |
|---|---|---|---|
| D37 | A synthetic company directory (`data/directory.json`) tells the gateway whether an address is one known employee or a list. | The question for a board is "who would read this?". The address alone does not say. | A rule on the address "all-staff". It closes the test, not the gap (D35). |
| D38 | An address that is not in the directory counts as an unknown audience, and personal data to it is refused. This includes addresses outside the company. | Fail closed (D7). A new list nobody registered must not be a way out. | Treating unknown internal addresses as single people. |
| D39 | Each labelled value is tied to the employee it is about (the ticket's requester). The gateway compares that employee with the reader. | This is what lets the ordinary reply through: an employee may be sent their own data. Without it, either every reply is held or none is. | Refusing all personal data in email. It would stop the service desk answering its own tickets (control C-07). |
| D40 | Three outcomes for email carrying personal data: refused if any reader is a list or unknown (rule P-012); held for a named person if every reader is a known employee but not only the person concerned (rule P-013); allowed if the only reader is the person concerned. | Matches the harm: thousands of readers, one wrong reader, the right reader. | One rule for all three. |
| D41 | Email to a list from an agent that has handled personal data is held even when no labelled value is found (P-013). | Same reasoning as D28: a disguised copy cannot be ruled out, and a mass mailing is rare enough for a person to release. Attack A-27. | Allowing it. |
| D42 | Email to one known employee with no labelled value found is not held. | This is the agent's daily work. Holding it would hold everything. | Holding every email from an agent that has handled personal data. |
| D43 | The gap D42 leaves is tested and published: A-29, disguised personal data to one single colleague, gets through. | D5 and D34. It is the least harmful version of the leak (one reader, effort needed to read it), but it is a leak. | Leaving it as an untested "known limit". |
| D44 | The agent's own statement of the data class is not used for email. | A compromised agent does not declare what it is leaking. | Refusing mail declared personal. It would also have changed six earlier results from "held" to "blocked" on the agent's word alone. |
| D45 | A dry run of an email with nothing stated now answers "deny" instead of "needs approval"; one existing test line was changed for this. | The dry run has no real call to read facts from, so the new rule fails closed. The path agents use (`execute`) is unchanged: an email with no recipient is still held (A-07). | Skipping the new rule in dry runs. |
| D46 | No delegation to a lighter model. | About 70 lines of security-sensitive logic. | |

### Steps and cost

| Step | What | Model | Tokens |
|---|---|---|---|
| 1 | Directory, two rules, reader check in the gateway and tools | Main (Fable 5.2) | About 1,400 estimated output |
| 2 | Four new attacks (A-26 to A-29), two new controls (C-07, C-08) | Main | About 700 estimated output |
| 3 | 11 new tests; ran tests and the campaign twice | Main | About 800 estimated output |
| 4 | README, this log | Main | About 1,700 estimated output |

Estimates cover text written, not reading and reasoning.

### Measured results

- 59 of 59 tests pass (48 before).
- Campaign: 29 attacks, 16 blocked, 11 held for a human, 1 capped, 1 breach (A-29). 8 of 8 legitimate actions allowed. Two consecutive runs give the same figures.
- A-25 (mailing list): blocked by P-012. A-26 (list hidden in blind copy): blocked by P-012. A-27 (disguised, to the list): held by P-013. A-28 (another employee's data to one colleague): held by P-013.
- Three earlier attacks (A-18, A-19, A-20) are still held, now under two rules (P-006 and P-013).
- Size: about 730 lines of Python.

### Open points

- A-29: disguised personal data to one single colleague.
- Held items are now 11 of 29. The approval screen is the most pressing missing piece: the control leans on people who today have no screen and no hint of what to look for.
- An employee's private address is not in the directory, so a reply there containing their own data is refused. Probably right, but it is a business decision nobody has taken.
- Attachments exist only as text in the call. Real attachments need their content read.
- The directory is a file. A real one changes daily and must itself be protected: whoever can edit it can turn a list into a "person".
- Held text is still written to the audit trail in full.
- Unchanged: one labelled source; tools simulated; legal references unverified; thresholds are assumptions.
- Published: M gave his go on 16 November 2026 and this session's changes were pushed to the public repository.

## Session 6, 16 November 2026

Goal given: the approval screen. Eleven of 29 attacks end with a named person, and that person had nothing to look at and no way to decide.

### What was missing

"Held for a human" was a verdict with nothing behind it. The held request was not kept anywhere a person could find it, any text given as approver was accepted, and a release had no link to the request it answered.

### Decisions

| # | Decision | Why | Alternative set aside |
|---|---|---|---|
| D47 | This session builds the queue, the decision and what the approver is shown. A clickable screen is the next step, not this one. | The logic is the control; the screen is its face. The repository shows formatted text pages but not web pages, so a generated page reaches a visitor today and a web screen would not. | A web page with buttons now. It needs a running server (against D1) and sign-in to mean anything. |
| D48 | The queue is read from the audit trail; nothing new is stored. | Same reasoning as D18 and D29: the held request is already there, tamper-evident. | A separate queue file. One more thing to protect. |
| D49 | The approver is the accountable owner of the agent in the registry. Only that role can release or refuse, and the gateway itself now ignores an approval from anyone else. | Until now any text counted as an approver. "A named person" has to mean the right named person. A wrong role's attempt is itself written to the audit trail. | A separate approver per rule. More precise, but the registry already names one accountable person per agent. |
| D50 | On release the gateway reads the request again and decides again. | The world may have changed while the item waited: kill switch pulled, limit reached. And if the stored request was altered, the checks run on what would really be carried out. Tested with a tampered record. | Carrying out the stored verdict. |
| D51 | An approver cannot release what a rule refuses. | Deny beats approval (unchanged), now also through the queue. | |
| D52 | The approver is shown: why it is held, in the words of each rule; and what to look for. For text: whose personal data was found and which fields, or, when nothing was found, which records the agent had read before writing. | This answers the open point from sessions 4 and 5: the approver had no hint. The record the agent read is the best lead to a reworded copy. | Showing the bare request. |
| D53 | In the campaign, legitimate requests that need approval now go through the queue: held, then released by their approver. | Before, the campaign passed the approval in directly, which did not test the route a real request takes. | |
| D54 | The published page carries the workload per approver. | Approval fatigue was an open item with no number. Now it has one: 9 of 11 waiting items fall on one role. | |
| D55 | Stated openly: version 0 does not verify who is at the keyboard. The approver states a role. | Without sign-in, "only the owner decides" is a rule about roles, not yet about people. | Leaving it implied. |
| D56 | No delegation. | The page wording could have gone to a lighter model, but it is about 40 lines generated from the same data as the decision logic; splitting it would have cost more than it saved (see session 1: 75,980 tokens for one small file). | |

### Steps and cost

| Step | What | Model | Tokens |
|---|---|---|---|
| 1 | Approval queue, owner-only decisions, hints (`approvals.py`); gateway link between a release and its request | Main (Fable 5.2) | About 2,300 estimated output |
| 2 | Command line: approvals, release, refuse; campaign routed through the queue; generated page | Main | About 700 estimated output |
| 3 | 8 new tests; ran tests and the campaign twice | Main | About 1,100 estimated output |
| 4 | README, this log | Main | About 1,500 estimated output |

Estimates cover text written, not reading and reasoning.

### Measured results

- 67 of 67 tests pass (59 before).
- Campaign figures unchanged: 29 attacks, 16 blocked, 11 held, 1 capped, 1 breach (A-29), 8 of 8 legitimate actions allowed. Three of the legitimate ones were held and then released by their approver through the queue.
- Waiting items by approver after the campaign: Head of IT Service Management 9, Head of OT Security 1, Chief Procurement Officer 1.
- Size: about 940 lines of Python.

### Open points

- No sign-in: the approver's identity is not verified (D55).
- No clickable screen; decisions are made on the command line.
- Nine of 11 items land on one person. Ways to reduce it (designed, not built): group identical items, let the owner name deputies, refuse outright what is held today where the evidence is strong (for example an outside address in blind copy).
- No time limit on a waiting item. It should expire and count as refused.
- The hints say whose data and which fields; they do not mark the place in the text.
- Held text is still written to the audit trail in full.
- Unchanged: A-29 open; one labelled source; tools simulated; legal references unverified; thresholds are assumptions.
- Published: M gave his go on 16 November 2026 and this session's changes were pushed to the public repository.

## Session 7, 16 November 2026

### What was done

1. The public pages were checked in a browser for the first time, signed out, as a visitor sees them: front page, this solution's page, the approver page, the red-team results, the agent inventory and the roadmap, at desktop width and at a narrow width.
2. `docs/roadmap.md` was corrected. It still listed building the Control Tower and running the first red-team campaign as future work.

### What the check found

- All tables display correctly at both widths. All links on the front page point to the right places.
- The roadmap was out of date (corrected in this session).
- Approver page, not yet corrected: decided items still carry the line "Waiting for"; items are numbered by audit record (1, 4, 7, 8, 73 ...), which looks arbitrary; synthetic email addresses become clickable mail links; the forged approval in item 73 gets no "Look for" hint; item 7 shows "The request: (nothing stated)".
- Red-team results: C-05 is listed before C-04.
- Not checked: this log, the business cases, the other two pages in `docs`, the nine "Designed" solution pages.

### Decisions

| # | Decision | Why | Rejected alternative |
|---|---|---|---|
| D57 | The roadmap gets an "In build" section that repeats the six next steps of this solution's page, in the same order. | Two published lists of next steps that differ would contradict each other in front of a visitor. | A separate, shorter list in the roadmap. |
| D58 | The roadmap carries no counts (attacks, rules, tests). It links to the pages that do. | Counts change with every run; the front page quotes none for the same reason. | Repeating the campaign figures. |
| D59 | The roadmap states that there is no data generator yet. | Checked in the repository: the data is five files written for this solution. The architecture page still describes one generator for all solutions, which is a design. | Leaving it unsaid. |
| D60 | The principle "after each fix, a new attack is written against its edge" is added to the roadmap. | Decided in sessions 4 and 5; it belongs with the other build principles. | |
| D61 | The corrections to the approver page are a separate step. | They change the page generator in `approvals.py`, which needs tests and a new campaign run. | Editing the generated page by hand, which the next run would overwrite. |

### Steps and cost

| Step | What | Model | Tokens |
|---|---|---|---|
| 1 | Browser check of six pages | Main (Fable 5.2) | Mostly input (page text and screenshots), roughly 60,000 estimated |
| 2 | Roadmap rewritten; this log | Main | About 1,300 estimated output |

### Measured results

- No code changed. Tests and campaign figures are as after session 6.

### Open points

- Approver page and red-team table corrections listed above.
- The architecture page says the plan is to build on an existing open-source enforcement layer; version 0 does not (D2). The two pages should say the same.
- A board deck of 30 slides was drafted from the elevator pitch and this repository. It is not part of the repository; a copy is in the Desktop folder under `board-deck`. It adds up the ten business cases (EUR 7,644,400 per year plus EUR 9M one-off, all illustrative assumptions) and the build estimates (595 to 835 hours).
- Published: M gave his go on 16 November 2026 and the roadmap and this log were pushed to the public repository.

## Session 8, 16 November 2026

### What was done

The last of the eight original features with nothing to show, the board dashboard, got a first working form: one generated page, `reports/board-latest.md`.

### Where the eight original features stand

| # | Feature | Status | Missing |
|---|---|---|---|
| 1 | Agent registry | Working | The card names a model class, not a specific model. |
| 2 | Policy gateway | Working, on own code | Not built on an open-source enforcement layer (D2); rules are a JSON file. |
| 3 | Human approval workflow | Working in part | Sign-in, a screen, expiry, deputies. |
| 4 | Tamper-evident audit trail | Working | A command that replays one decision for an auditor. |
| 5 | Risk classification | Working in part | Fixed rules, not an agent; human sign-off is an empty field; legal references unverified. |
| 6 | Red-team agent | Working in part | A script on demand, not an agent that invents attacks every night. |
| 7 | Kill switch and circuit breakers | Working in part | Nothing trips the switch automatically: no cost budget, no anomaly detection. |
| 8 | Board dashboard | Working in part (this session) | Quarterly schedule, trends, cost and benefit per agent. |

### Decisions

| # | Decision | Why | Rejected alternative |
|---|---|---|---|
| D62 | The board report is a generated text page in `reports/`, like the approver page. | The repository shows formatted text pages to a visitor without anything running (D47). | A web dashboard, which needs a server (against D1). |
| D63 | The report measures and stores nothing new. It is put together from the registry, the classifier and the latest campaign results. | One source for every figure: the report cannot disagree with the pages it summarises. | A separate set of board figures. |
| D64 | "Contained" is defined on the page: refused outright, held for a named person, or stopped at the daily allowance. The share is shown as a count first (28 of 29), then a percentage. | A bare pass rate hides what counts as a pass. Held is not the same as refused, and the breakdown tables show the difference. | A single percentage. |
| D65 | The "points for the board's attention" are derived from the data: open breaches, more than half of the waiting actions on one role (threshold is an assumption), high-risk agents, tiers without sign-off, agents registered but not approved. | A fixed list would go stale. If a point no longer applies, it disappears from the page by itself; a test checks that a campaign without breaches reports no open finding. | Hand-written findings. |
| D66 | The campaign results file now also carries the waiting actions per approver and the number of rules. | The board report needs both, and the campaign already knows them. | Parsing the approver page. |
| D67 | The report's time stamp is the campaign's. | Running `board` twice gives the same page. | A second time stamp. |
| D68 | The page says what it does not cover: scripted attacks, simulated tools, no trend, no cost and benefit, no detection of unregistered AI use. | A board page that looks complete would overstate version 0. | Leaving the limits to the other pages. |
| D69 | No delegation. | About 120 lines that summarise security results; the wording of the findings is the control. | |
| D70 | The board deck is local only: kept in the Desktop folder, updated when a feature is added or its status changes, never pushed. A `.gitignore` at the top of the repository excludes the folder `board-deck`. | M's decision on 16 November 2026. The deck is a selling document for a meeting, not part of the public proof. The exclusion guards against a later session copying the whole Desktop folder into a clone. | Relying on the handover note alone. |

### Steps and cost

| Step | What | Model | Tokens |
|---|---|---|---|
| 1 | Read the command line, registry, campaign and approvals code | Main (Fable 5.2) | Input only, about 9,000 estimated |
| 2 | `board.py`, link into the campaign and the command line, `KillSwitch.stopped` | Main | About 2,400 estimated output |
| 3 | 6 new tests; ran tests and the campaign | Main | About 800 estimated output |
| 4 | README, roadmap, this log | Main | About 1,600 estimated output |

### Measured results

- 73 of 73 tests pass (67 before).
- Campaign figures unchanged: 29 attacks, 16 blocked, 11 held, 1 capped, 1 breach (A-29), 8 of 8 legitimate actions allowed. Contained: 28 of 29.
- Agents by proposed tier: 0 prohibited, 1 high, 10 limited, 5 minimal. By autonomy: 7 advise, 3 act with approval, 6 act. 15 of 16 approved.
- Size: about 1,100 lines of Python.

### Open points

- The report is generated on demand; "quarterly" is a schedule nobody has built.
- No trend, because the campaign keeps no history.
- The share of attacks contained depends on which attacks are in the list. It is a measure of this campaign, not of safety.
- Agents appear by technical id in the per-agent table and by name elsewhere.
- Three points M was shown before publishing and that were left as they are: open finding A-29 starts with "The same, but disguised", taken from the campaign list; agents appear by technical id in the per-agent table; the 97% is prominent in the first table.
- Published: M read the final text of the board report and gave his go on 16 November 2026; this session's changes were pushed to the public repository.

## Session 9, 16 November 2026

### What was done

The board report page was read in a browser on the public site for the first time, and the list of small faults from the first browser check (session 7) was worked off on the approver page and the red-team results page. No rule, no decision logic and no campaign figure changed; only how the pages are written.

### What the browser check of the board report showed

- The page shows as intended: nine-row summary, five points for the board, six tables, and the three links (agent inventory, red-team results, approver page) all lead to the right pages.
- Nothing on it becomes a mail link.
- Three points of wording were seen and left for M to decide, not changed: with a single high-risk agent the sentence still starts "They may read on their own"; the answer to "Is the record of decisions unaltered?" is the technical phrase "chain intact"; the per-agent table shows technical ids (already left as it is in session 8).

### Decisions

| # | Decision | Why | Rejected alternative |
|---|---|---|---|
| D71 | Items on the approver page are counted in the order of the page ("Waiting 5 of 11", "Decided 1 of 3"). The audit record number moves to its own line and is what the approver types to release or refuse. | A reader saw items 1, 4, 7, 8, 73 and asked where the others were. The number that looked like a count was an audit reference. The command still needs that reference, so it stays, named for what it is. | Renumbering the audit trail, which would break its chain; hiding the record number, which would leave the approver nothing to type. |
| D72 | Decided items say "Approver" and "Why it was held", not "Waiting for" and "Why it is held". | They are no longer waiting. | |
| D73 | Email addresses on the approver page are written as literal text. | The public site turned the synthetic addresses into mail links that a visitor could click. | Leaving the addresses out, which would hide what the approver has to judge. |
| D74 | When a request carries its own "approved by", the approver is told: the agent wrote that claim, it counts for nothing, only a release from the queue by the accountable owner approves the action. | The forged approval (attack A-13) was held correctly but shown without comment, so the approver could have read the forged line as a fact. | |
| D75 | A request without details says so in words ("the agent stated no details") instead of "(nothing stated)". | The old line read like a fault of the page. | |
| D76 | The red-team results page lists cases by id. The campaign still runs in the order of `data/attacks.json`, and the results file keeps that order. | C-05 was shown before C-04. The run order is deliberate and was not touched; only the listing is sorted. | Reordering the campaign file, which would change the audit record numbers of the run. |
| D77 | No delegation. | About 30 changed lines in the page generator, next to the approval logic; a hand-over would have cost more than the work. | |

### Steps and cost

| Step | What | Model | Tokens |
|---|---|---|---|
| 1 | Read handovers g and h, the board report in the browser, `approvals.py`, `redteam.py`, the command line and the tests | Main (Fable 5.2) | Input only, about 16,000 estimated |
| 2 | Changes to `approvals.py` and `redteam.py` | Main | About 900 estimated output |
| 3 | 3 new tests and 3 added checks in an existing test; ran tests and the campaign | Main | About 500 estimated output |
| 4 | This log | Main | About 900 estimated output |

### Measured results

- 76 of 76 tests pass (73 before).
- Campaign figures unchanged: 29 attacks, 16 blocked, 11 held, 1 capped, 1 breach (A-29), 8 of 8 legitimate actions allowed. The campaign was run again to regenerate the pages, so the time stamp on all three pages is new.
- Size: about 1,100 lines of Python (1,120).

### Open points

- Published: M was shown the final text of the changes and gave his go on 16 November 2026. The check of the corrected pages in a browser follows the push.
- `docs/architecture.md` still says the plan is to build on an existing open-source enforcement layer; version 0 does not. Not part of this session.
- The three wording points on the board report listed above wait for M.

## Session 10, 16 November 2026

### What was done

Three small points left open by session 9 were closed: one sentence in `docs/architecture.md` and two wordings on the board report. The board deck, which is local and not part of the repository, was then brought in step.

### Decisions

| # | Decision | Why | Rejected alternative |
|---|---|---|---|
| D78 | `docs/architecture.md` now says that version 0 runs on the project's own small gateway, that it has a single entry point so an open-source enforcement layer can replace it later, and that this replacement is not built. | The page still described the earlier plan as the current one (see D2). The Control Tower page already said the opposite. | Removing the mention of an open-source layer, which would hide a choice a technical reader will ask about. |
| D79 | On the board report the answer to "Is the record of decisions unaltered?" is given in words: "Yes. Every entry was checked against the one before it and none was changed." If the check fails the answer starts with a bold "No" and gives the technical result. | "chain intact" is the tool's phrase, not a board answer. The technical phrase stays on the red-team results page. | Changing the audit check's own message, which other pages and a test rely on. |
| D80 | With exactly one high-risk agent the sentence reads "It may read on its own; every other action it takes waits for a named person"; with several it stays "They may read on their own". | The page said "They" about one agent. | |
| D81 | No delegation, although the task was small enough for a lighter model. | Three sentences and one test; starting a second model would have cost more than the change (see session 1). M was told beforehand that a lighter model would do. | |

### Steps and cost

| Step | What | Model | Tokens |
|---|---|---|---|
| 1 | Read `docs/architecture.md`, `board.py`, decision D2 and the deck's build notes | Main (Fable 5.2) | Input only, about 6,000 estimated |
| 2 | Changes to `architecture.md` and `board.py`, 1 new test; ran tests and the campaign | Main | About 500 estimated output |
| 3 | This log | Main | About 600 estimated output |

### Measured results

- 77 of 77 tests pass (76 before).
- Campaign figures unchanged: 29 attacks, 16 blocked, 11 held, 1 capped, 1 breach (A-29), 8 of 8 legitimate actions allowed. The campaign was run again, so the time stamp on the report pages is new.
- Size: about 1,100 lines of Python (1,129).

### Open points

- `docs/architecture.md` lists a red-team scoreboard for "nightly attacks" and a one-page board dashboard among the planned features. Both are still correct as plans; the risk half of the board page now exists in a first form and the page does not say so.
- Agents still appear by technical id in the per-agent table of the board report (left as it is by M in session 8).
- Published: M was shown the final text of the three wordings and gave his go on 16 November 2026.
- The board deck (local, not in the repository) was brought in step: the test count on the evidence slide and in its speaker note is 77. The PowerPoint file was rebuilt from the saved build scripts, which confirms they work. The private online copy of the deck could not be changed from this session and still says 73.

## Running totals after session 10

| | Value | Kind |
|---|---|---|
| Tokens used by the lighter model (one delegated task) | 75,980 | Measured |
| Text written by the main model, session 1 | about 11,300 tokens | Estimated from file size |
| Text written by the main model, session 2 | about 3,350 tokens | Estimated from file size |
| Text written by the main model, session 3 | about 4,300 tokens | Estimated from file size |
| Text written by the main model, session 4 | about 5,100 tokens | Estimated from file size |
| Text written by the main model, session 5 | about 4,600 tokens | Estimated from file size |
| Text written by the main model, session 6 | about 5,600 tokens | Estimated from file size |
| Text written by the main model, session 8 | about 4,800 tokens | Estimated from file size |
| Text written by the main model, session 7 | about 1,300 tokens for the repository, about 9,000 for the deck | Estimated from file size |
| Text written by the main model, session 9 | about 2,300 tokens | Estimated from file size |
| Text written by the main model, session 10 | about 1,100 tokens for the repository | Estimated from file size |
| Total tokens of the main model including reading and reasoning | Not known from inside the session | Take it from the usage screen |
| Python code | about 1,100 lines | Measured |
| Tests | 77 of 77 passing | Measured |
| Red-team attacks | 29: 16 blocked, 11 held, 1 capped, 1 open breach (A-29) | Measured |
| Commits to the public repository | 13 | Measured |

## Where to continue

1. Approval screen with buttons and sign-in, on top of the queue built in session 6; reduce the load on one approver.
2. Breach A-29: disguised personal data to one colleague. Needs a second check of outgoing text.
3. Label more sources and shared stores.
4. Then: nightly run with history, model-driven red-team agent, more rules, board one-pager, approval screen, first real tool.
5. Still to verify against the official texts: EU AI Act article references and ISO/IEC 42001 control names in `classifier.py`.

## 18 November 2026: two cards added for solution 02 (the solution itself stays paused)

- Decision by M: the two agents that the build of solution 02 adds, the Office-side First Response Agent and the Response Challenger, are entered in this registry, not kept in a list of their own. Reason: one registry is the single place agents are listed.
- Changed: `data/agents.json` 18 to 20 cards; four counts in `tests/test_control_tower.py`; `reports/agent-inventory.md` and `reports/board-latest.md` regenerated by `python -m control_tower inventory` and `board`; one figure in `README.md`. The red-team campaign pages are unchanged.
- Measured: 77 of 77 tests pass in the assistant's workspace.
- Limit found: the classifier proposes the tier "minimal" for the first-response agent, which suspends accounts on its own. It follows the use-case flags only. Fix designed, not built: an internal rating by reach of action beside the legal tier.
- Not changed: the wording "agents" for registry cards whose solutions run no model yet. Still an open point of the project handover.
- Details and tokens: `solutions/02-ot-it-convergence-sentinel/BUILD_LOG.md`, session 4, third part.

## 18 November 2026, second entry: reach of action, and what stands behind each card

Agreed with M as step 1 of five: update solution 01, then solution 02, then the slides.

| Decision | Why | Alternative set aside |
|---|---|---|
| A second rating beside the legal tier: reach of action, in four levels (1 reads only, 2 writes or proposes inside the company, 3 acts on accounts, systems or money, 4 can stop production), worked out from the card's permission list by fixed rules (`control_tower/reach.py`). | The legal tier called the first-response agent of solution 02 "minimal" although it suspends accounts on its own. A board asks what an agent could do if it went wrong, which the law's categories do not answer. | Changing the legal classification to make the result look right. |
| A tool the rating does not know counts as level 3. | A new permission must never look harmless by default. | Rating unknown tools as level 1. |
| The board page lists every card at level 3 or more that is registered to act without a person. | It is the short list a board should see. Today: the first-response agent (in build) and the Service Desk Resolution Drafter (designed). | A table only. |
| Every card carries a field `today`: designed, fixed code, agent in build, or agent working. The registry refuses a card without it. Inventory and board page show it; the solution page defines the word "agent". | The charter: an agent is a language model in a loop; fixed code is never called an agent. The pages spoke of "18 agents" although no model runs behind any card. Now: 3 agents in build, 6 steps of fixed code, 11 designed. | Renaming the registry; removing cards of fixed code (they still need an identity at the gateway). |

- Changed: `control_tower/reach.py` (new), `registry.py`, `board.py`, `__main__.py` (inventory), `data/agents.json` (field `today` on 20 cards), 5 new tests, `README.md`, `reports/agent-inventory.md` and `reports/board-latest.md` regenerated. The red-team campaign pages are unchanged.
- Measured: 82 of 82 tests pass in the assistant's workspace; solution 02 still 75 of 75.
- Limits: the reach rating looks at permissions only, not at how often or how widely a tool is used; like the legal tier it has no recorded human sign-off. The elevator pitch and the board deck (both outside the repository) still use the old wording.
- Tokens, estimated: input about 25,000, output about 6,000, main model (Fable 5.2). A lighter model could have done the page regeneration, not the rating design.

## 19 November 2026: registry changes made from solution 02

Recorded in solution 02's BUILD_LOG, session 5 (D60, D61). In `data/agents.json`: `cases.read` added to `ot-response` and `ot-challenger`, `cases.write` to `ot-briefing` (reach of action unchanged); the three solution 02 agents move from "agent in build" to "agent working" after five recorded runs with a real model. `reports/agent-inventory.md` and `reports/board-latest.md` regenerated; two expectations in `tests/test_control_tower.py` updated. 82 of 82 tests.

## Session 11, 20 November 2026: the Control Tower and the open standards (step 7 of the project, first part)

### What was done

Dated research on the current agent-governance standards and toolkits, recorded outside the repository (project research note of 20 November 2026; its sources are summarised below). Decisions taken on what the Control Tower adopts, wraps and keeps. Pages updated so that every page says the same thing. No code changed in this session: everything new below is **Designed**, and the shared agent harness is the next build.

### What the research found on 20 November 2026

- **OWASP Agent Control Standard (ACS)**, published by the OWASP GenAI Security Project on 1 September 2026, specification v0.1.0, next version targeted for March 2027, no 1.0 date. A wire specification: a separate "Guardian" receives what an agent is about to do and answers with one of five decisions: allow, deny, modify, ask (a human, agent or service approves) or defer. Nineteen lifecycle hooks; the reference implementation evaluates two live, the tool-call request and the tool-call result. The mandatory baseline (ACS-Core) is the hooks and decisions, a JSON-RPC 2.0 wire format with an HMAC-SHA256 signature on every message, and an audit chain. Optional: tracing as OpenTelemetry spans and OCSF events, and an Agent Bill of Materials (AgBOM). Code and schemas Apache 2.0. A conformance harness tests a running Guardian over HTTP. Conformance claims are self-declared in v0.1.0. Source: https://github.com/Agent-Control-Standard/ACS, https://genai.owasp.org/resource/agent-control-standard-acs/
- **Microsoft Agent Governance Toolkit**, MIT, still public preview; latest release v4.1.0 of 9 June 2026 on its release page. Policy engine, kill switch, MCP gateway, adapters for 14 agent frameworks. Source: https://github.com/microsoft/agent-governance-toolkit
- **OWASP Top 10 for Agentic Applications (2026)**, released 9 December 2025: the list vendors and auditors map agent risks to.
- **OpenTelemetry generative-AI conventions** moved to their own repository on 12 June 2026 and were all in Development status as of July 2026.
- **Model Context Protocol** current specification 2026-07-28 (stateless core). **A2A** v1.0 since March 2026, Linux Foundation.
- **EU AI Act**: Regulation (EU) 2026/1744 (Digital Omnibus), in force 27 July 2026; high-risk obligations from 2 December 2027 (Annex III) and 2 August 2028 (Annex I), per several secondary sources; the Official Journal text was not read.

### Decisions

| | Decision | Why | Alternative set aside |
|---|---|---|---|
| D82 | The Control Tower stays the company's own code. | Owning the control layer is what this project sells, and the toolkits found are previews that change shape every few weeks (AGT v1.0 to v4.1 between March and June 2026). | Adopting the Microsoft toolkit as the core. |
| D83 | The Control Tower follows the OWASP Agent Control Standard for the whole system: the gateway is to become an ACS Guardian, and every agent of every solution reaches it through the ACS tool-call request and result hooks of the shared harness. Status: **Designed**. | The gateway already sits where ACS puts its Guardian: one checkpoint before every tool call, deciding allow, deny or hold. Following the standard means a company keeps its own rules and can still put any agent framework, or a third-party Guardian, on the same wire. Board line: owned by the company, built to the open standard. | Our own interface only, which would lock each company into our harness. |
| D84 | Our three decisions map to ACS as: allow to `allow`, refuse to `deny`, hold for a named person to `ask`. The daily volume limit answers `deny` once the allowance is spent. `modify` and `defer` are not used in version 0. | The mapping is exact for what the gateway does today. Not using `modify` keeps the rule that the gateway never rewrites what an agent asked for without a person. | Inventing a fourth decision outside the standard. |
| D85 | What will be claimed, and when: until the ACS conformance harness has run against the gateway and its result is published, every page says "designed to follow" or "in build", never "conformant". Conformance in v0.1.0 is self-declared, so the published test result is the proof, not the claim. | Charter: nothing is described as built before it is built. | Saying "ACS-compliant" from the design alone. |
| D86 | Known gaps to ACS-Core, published now: the JSON-RPC 2.0 wire format, the HMAC-SHA256 signature on every message, and the tool-call result hook (the gateway checks every request before the tool runs; it does not yet check what a tool returns). Our audit trail is hash-chained; whether that meets the ACS audit chain is to be checked against its schema. | Gaps are published, not hidden, each with its fix (charter section 7). | Listing them only after the build. |
| D87 | The registry exports an AgBOM-shaped inventory (models, tools, dependencies per card). **Designed.** | Optional in ACS, cheap for us: the registry already holds the facts. | |
| D88 | The record follows the OpenTelemetry generative-AI names, pinned to a dated commit and marked "Development status". **Designed.** | A company can send our record to the monitoring it already runs; the pin protects against names that still move. | Our own names only. |
| D89 | Every tool is described in the shape of MCP 2026-07-28; agent-to-agent cards in A2A v1.0 shape are designed for the solutions that need them (War Room, S&OP). **Designed.** | A company can replace our simulated tools with its own MCP servers without touching the agents. | Running a real MCP server now, which no solution needs yet. |
| D90 | The Microsoft Agent Governance Toolkit is an optional adapter, never a dependency. **Designed.** | Shows the tower can sit beside Microsoft's toolkit; no lock-in, and the blueprint stays runnable on a plain Python install. | A dependency on a preview package. |
| D91 | Every control is to be mapped to the OWASP Top 10 for Agentic Applications (2026), and the classifier's dates to Regulation (EU) 2026/1744. **Designed.** | The language auditors and vendors already use. | |
| D92 | No delegation. | The decisions depend on the whole project's context; the page edits are short. A lighter model could have run the searches. | |

### Changed

`README.md` (top), `docs/architecture.md`, `docs/roadmap.md`, this folder's `README.md`, and solution 02's `README.md` (one sentence on the standard, and the invented vendor names of the board deck's tool slide, which the page did not carry yet). No code, data or test changed.

### Measured

Tests run in the assistant's workspace after the page edits: Control Tower 82 of 82, solution 02 92 of 92. No figure changed.

### Steps and cost

Tokens, estimated (no tool reports them in this session): research about 60,000 in and 5,500 out; this session's repository work about 45,000 in and 9,000 out. Main model.

### Where to continue

Step 7, second part: take the agent loop, the model connector and the case memory out of solution 02 into one shared harness whose tool calls reach the gateway through the ACS tool-call hooks (D83, D84); solution 02 keeps passing its 92 tests on it. Then run the ACS conformance harness against the gateway and publish the result, including what fails.

## Session 12, 20 November 2026: the shared agent harness (step 7 of the project, second part, fast version)

Mario's instruction: finish this step as fast as possible, then solution 10. Scope taken from the project handover of 20 November (c).

### Decisions

| No. | Decision | Why | Set aside |
|---|---|---|---|
| D93 | The harness lives in `shared/harness/` at the top of the repository, as a package named `harness`, and does not import the Control Tower: a solution hands it a gateway. | It belongs to no single solution, and a company can put its own control layer behind the same hook. | Keeping it inside solution 01 (it would tie every agent to our gateway's code); a pip-installable package (not needed for a blueprint). |
| D94 | Moved: the agent loop and the model connector (whole files), the word-limit and figure checks, the generic part of the case book, and three small pieces of the decision page (quotation, agent turns, tokens). Solution 02 keeps `sentinel/loop.py` and `sentinel/model.py` as two-line pointers. | The 92 tests import from those names and had to pass unchanged. | Changing the tests' imports. |
| D95 | What stays in solution 02: which earlier cases matter tonight, what a case records, and the body of the page. | They speak of devices, accounts and production lines; a ledger or a war room will ask different questions. Moving them would have been a shared name over Sentinel code. | A generic "decision page" class, before a second solution shows what is really common. |
| D96 | One function, `tool_call_request(gateway, announcement)`, is the only place in the harness and in solution 02 that calls `Gateway.execute`. It answers `allow`, `deny` or `ask` and carries the gateway's own verdict unchanged. `act` is built on it. The two direct calls that filed held steps (`response.py`, `decision.py`) now go through it too. | D83, D84. One door is what makes the later wire format a change in one file. | Leaving the two direct calls (they would bypass the hook). |
| D97 | An answer the harness does not know is treated as `deny`. | Closed by default. | |
| D98 | Not built, and said so on every page: the ACS wire format, the signature, the result hook, the conformance test (D85, D86 unchanged). | Fast version; the charter's rule on status. | |
| D99 | The key file variable gets a neutral name, `HALDEN_MODEL_KEY_FILE`; `SENTINEL_MODEL_KEY_FILE` still works. | Solution 10 should not need a variable named after solution 02; Mario's PowerShell line keeps working. | |
| D100 | No run with a real model. | Behaviour did not change: 92 of 92 unchanged tests, and the rule-based run gives the same result. | |
| D101 | Pages 03 to 09 get one line saying their agent list will change; they are rewritten when each is built. | Removes the contradiction with the definition of an agent at little cost. | Rewriting eight pages now. |

### Measured

In the assistant's workspace (Python 3.13): Control Tower 82 of 82, solution 02 92 of 92 with no test file changed, shared harness 15 of 15. The hook tests cover: allow to `allow`; a tool not on the permission list, an unregistered agent and a stopped agent to `deny`; a held step to `ask`, allowed when the accountable person makes it; the daily volume limit to `deny` (V-002, and V-001 for a request without a row count).

### Steps and cost

Tokens, estimated (no tool reports them in this session): about 150,000 in and 22,000 out, main model. The file moves and test runs would suit a lighter model; the hook and what to leave in solution 02 would not.

### Where to continue

Solution 10, the AI Value Ledger, on this harness. For the finish: the ACS wire format and signature in `shared/harness/hooks.py`, then the conformance test.
