# Build log: Self-Healing Service Desk

What was decided while building this solution, why, and what was set aside. Tokens are estimated where no tool reported them.

## Before the build, 20 November 2026

Research, the angle and the article. The article "Who checks the ticket that AI agent closed?" was published on LinkedIn on 20 November 2026, before the build, at Mario's instruction, with the status line "The two agents, the autonomy ladder and the red-team attacks are designed, not built yet." That line is replaced when the build is finished.

Decisions of that step, agreed by Mario on 20 November: the angle "the agent did nothing it was not allowed to do"; a resolution agent and a verifier that never closes a ticket, in place of the triage agent of the September design; an autonomy ladder per ticket type; a learning loop; a red team fed by published incidents; plant-floor and security tickets handed to the Sentinel; the suite reached through one connector, nothing replaced.

Tokens for that step, estimated, main model: about 330,000 in, 22,000 out.

## Session 1, 22 November 2026: build step 1, the foundations

No model is involved in anything built in this session.

### Decisions

| | Decision | Why | Set aside |
|---|---|---|---|
| D1 | The registry card `sd-triage` is renamed `sd-verifier`, with a new purpose, autonomy `advise`, and the tools `ticket.read`, `kb.read`, `verification.write`. | The Control Tower's count stays at 20 cards, and its second service desk agent now sits where the gap is. The card has no tool that changes a ticket, which is what makes "never closes a ticket" a control and not a promise. | A new card next to `sd-triage`: a 21st card for an agent that is no longer planned. |
| D2 | Halden's suite is called Quillfield Service Desk, its own agent Quillfield Auto-Resolve. | Charter: invented, descriptive names, checked by web search. Two searches on 22 November 2026 found no service desk product under the name. | "Tessera", too close to the real product Tesseron; "Deskline", too generic to check. |
| D3 | The answer key is a separate file that the suite stand-in never loads and the connector never serves. | A verifier that could read the label would prove nothing. | A `flawed` field on the ticket, hidden by the connector. One mistake in the connector would leak it. |
| D4 | 26 of 150 closed tickets carry a planted flaw (16 fix did not hold, 5 requester not entitled, 5 record mismatch); 16 of the 26 were closed by the stand-in for the suite's own agent. The page says these are design choices, not findings about a product. | The verifier needs something to find in step 2, in all three kinds, in closures by an agent and by people. | Equal flaw rates for the agent and for people: it would hide the pattern the article is about, an error repeated across a ticket type. |
| D5 | A follow-up ticket is never linked to the ticket it follows. | In a real desk the person who comes back opens a new ticket in their own words. The link is what the check has to find. | A `follow_up_of` field. |
| D6 | One test checks the answer key against the evidence in both directions: every planted flaw can be found from what the suite shows, and no sound ticket looks flawed. | Without it, the verifier in step 2 could be marked wrong for a correct finding. | Trusting the generator. |
| D7 | The ladder's thresholds, starting rungs, ceilings and sampling shares are data, and labelled as assumptions. | Charter: every figure is measured or labelled. A company enters its own. | Constants in code. |
| D8 | A step down is taken by code on the finding; a step up only by the role in the briefing, one rung at a time; the count of cases starts again after every move. | "Autonomy is earned and can be lost" must not depend on anyone being available to take it away. One rung at a time, because the evidence at one rung says nothing about the next. | The verifier moving a type itself: an agent would then decide another agent's autonomy. |
| D9 | A serious finding drops a type to Propose, not to Watch. | At Propose a person carries out every action, which removes the risk; the agent's proposals still produce evidence for the way back up. | Watch: safe, and no evidence would accumulate where it is most needed. |
| D10 | Ceilings: identity-touching types stop at Act with check; a change of recovery contact stops at Propose. | The Meta case began with a new email address attached to an account. No amount of clean history should let that happen without a person. | No ceiling, evidence only. |
| D11 | The four types the suite's own agent already closes alone start at Act with check. | It describes a company on the first day: the autonomy was granted on confidence, so everything is checked until there is evidence. | Starting them at Act alone, which would repeat the state the article criticises; or at Watch, which would pretend the suite's agent is not running. |
| D12 | The connector asks the ladder first, then the Control Tower, then the suite. | If the Control Tower came first, its audit trail would show "allow" for an action the ladder then refused. | Control Tower first. |
| D13 | An agent whose card allows no change is not sent to the ladder; the Control Tower refuses it (rule PERM-1). | First version: the verifier on a Watch type was told "a step up is approved by...", as if a step up could ever let it close a ticket. Found when the command line was tried. | Leaving the wording. |
| D14 | Ladder moves and ladder refusals are written to the Control Tower's audit trail, with the source `autonomy-ladder`. The ladder also keeps its own record of cases and moves. | One record of who decided what. No new registry identity was needed. | A 21st card for the ladder. |
| D15 | The role that decides is "Head of IT Service Management": the accountable owner on both registry cards. | The gateway accepts an approval only from a card's accountable owner, and that title is in 82 Control Tower tests. The article says "Head of IT Service", the same role in shorter words. | Renaming the owner on the cards to match the article. |
| D16 | All five reading operations count as `ticket.read` at the Control Tower. | A real suite keeps its user and asset records itself. It keeps the cards unchanged. | A `directory.read` permission on both cards. |
| D17 | Where a handed-over ticket goes is set by the ticket type, whatever the agent names. | An agent talked into "hand it to me" must not be able to redirect a security ticket. | Trusting the `to` the agent gives. |
| D18 | The suite's problems are the harness's `ToolProblem`. | In step 2 the agent loop hands them back to the model, which can try something else. | A separate exception to translate later. |
| D19 | The solution page carries a dated list of sources. | The published article's reference 4 says the full source is in the repository. Project documents are never pushed, so the page now makes that sentence true. | Pushing the research note. |
| D20 | Tickets are in English only. | The check, not translation, is what this solution shows. | The September design's "languages of all sites". |

### What was checked

- Five test suites in the assistant's workspace on Python 3.13: Control Tower 82, solution 02 92, shared harness 15, solution 10 34, this solution 31.
- The first run of the new tests failed twice, correctly: the verifier's card still held `ticket.update` after an edit that had not applied. Corrected, and the test that caught it stays.
- The Control Tower's inventory, red-team campaign and board page were generated again after the card change. The campaign's result is unchanged: 29 attacks, 16 blocked, 11 held, 1 capped, 1 breach (A-29, open, published). On the board page, "advise only" moved from 10 to 11 cards and "act" from 7 to 6.
- Every figure on the solution page was read from `python -m servicedesk tickets` or from a test.

### Open, for the next steps

- The value ledger's portfolio names "Head of IT Operations" as the owner of `sd-resolution`; the registry says "Head of IT Service Management". To be aligned in step 4, when the portfolio is touched and its recorded runs can be regenerated.
- The verifier's findings have no store yet. `verification.write` is on the card for step 2.
- Applying a rung to the suite's own agent is a setting inside a real suite. Designed.

### Tokens

| Step | What | How | Model | Tokens |
|---|---|---|---|---|
| 1 | Charter, handover, research note and article draft read; repository cloned and read (harness, Control Tower, solutions 02 and 10) | Project documents, GitHub | Main (Claude Fable 5.2) | Input about 110,000, output about 3,000, estimated |
| 2 | Vendor name checked | Five web searches | Main | Input about 45,000, estimated |
| 3 | Data generator, suite stand-in, ladder, connector, command line, configuration files | Written in the workspace | Main | Output about 22,000, estimated |
| 4 | 31 tests written and run; registry card renamed; Control Tower reports generated again | pytest | Main | Output about 9,000, estimated |
| 5 | Solution page, business case, this log, root page and roadmap | Written in the workspace | Main | Output about 8,000, estimated |

A lighter model could have done steps 1, 2 and 5 and the data generator. The ladder's rules and the order of the checks in the connector are the work that needed the main model.

## Session 2, 22 November 2026: build step 2, the two agents

The two agents are built on the shared harness and tested on prepared replies. No real model ran in this session: real runs need Mario's key, and nothing is claimed here about what a model does.

### Decisions

| | Decision | Why | Set aside |
|---|---|---|---|
| D21 | Each agent works one ticket per run. The tools that change a ticket take no ticket number. | A short loop is easier to read on the page and cheaper per ticket; and an agent that cannot name another ticket cannot be talked into changing one. | One long run over a batch of tickets. |
| D22 | "Who is asking" is a rule in the connector, not an instruction to the agent: a fix on an identity-touching type needs the suite's own confirmation that the requester is the owner. A tenth connector operation asks the owner's registered phone. | This is the check that was missing behind Meta's assistant. A briefing sentence can be argued with; a refused call cannot. It is also what the red team of step 3 will attack. | Leaving it to the model's judgement and testing that in step 3. |
| D23 | Open identity tickets now show what the suite confirmed at intake (signed-in session, or none yet). | The rule in D22 needs a fact to read. The seed and every other field are unchanged. | A confirmation invented at the moment of the fix. |
| D24 | The hand-in of the resolution agent must name the last step the suite recorded. | "The record says what was done" applies to our own agent first. | Trusting the agent's summary. |
| D25 | A finding is accepted only after three sources were read in that run; "did not hold" must name a later ticket a tool returned; "held" is refused before the seven days are over. | A finding is evidence for a decision about autonomy. It has to rest on something the page can show. | Free-text findings scored afterwards. |
| D26 | What a finding means for the ladder is fixed code (`findings.py`). The verifier answers three questions; it does not rule. | An agent must not decide another agent's autonomy, even indirectly. | An "outcome" field in the hand-in. |
| D27 | "Cannot tell" is a valid answer, counts for nothing on the ladder, and puts the ticket on a list to be checked again. | A closure by our own agent, checked the same morning, cannot honestly be called held. The alternative teaches the verifier to guess. | Forcing yes or no. |
| D28 | A proposal for a permanent fix is written to the knowledge base through the Control Tower's existing rules: held for a named person (P-011), refused with personal data (P-010). | The approval path already exists and is already tested in solution 01. Nothing new had to be trusted. | A separate approval mechanism in this solution. |
| D29 | An approved proposal adds a standing instruction to the briefing in force. The briefing file is not rewritten. The instruction is shown to both agents and enforced by the connector. | "A briefing change changes behaviour without code" should hold even when a model ignores what it reads. | Showing the instruction to the model only. |
| D30 | One waiting proposal per incident. | Found while running the third scenario: a corrected proposal was stored next to the first, and the approval went to the wrong one. | Letting the decider sort out duplicates. |
| D31 | Case memory is written by fixed code under the identity of the agent whose work it records; `cases.write` was added to both cards. | The same pattern as the Sentinel's case memory. The verifier's card still holds no tool that changes a ticket. | A new registry card for a case writer. |
| D32 | In a scenario, a decision of the Head of IT Service Management is given by the scenario file, and the page says so in the same sentence. | The third scenario needs the approval to show the instruction in force. Hiding who gave it would be the kind of record mismatch this solution is about. | Stopping the scenario and waiting for a person, which a recorded run cannot do. |
| D33 | The verifier's findings are compared with the answer key by fixed code after the agents have finished, and the result is on the page. | It is the one measured figure about the verifier that a real run will produce. | Reporting only that the run ended. |
| D34 | Both cards now say "agent in build", not "working". | Charter: working means recorded runs with a real model. | Calling them working on prepared replies. |
| D35 | The prepared replies of each scenario include one hand-in the harness refuses, and its correction. The sample pages carry a line saying they prove nothing about a model. | The sample pages should show the controls acting, and nobody should mistake them for a result. | Clean scripts that only show the happy path. |

### What was checked

- Five test suites: Control Tower 82, solution 02 92, shared harness 15, solution 10 34, this solution 61 (31 foundations, 30 agents).
- The three scenarios run to their page on prepared replies; the three sample pages were read in full.
- Reading the third sample page found the duplicate proposal (D30) and a doubled sentence in the decision line; both corrected.
- The Control Tower's reports were generated again. Campaign unchanged: 29 attacks, 1 open breach. Board page: 4 agents working, 2 in build, 6 steps of fixed code, 8 designed.

### Not known

- Whether a real model reads the three sources before filing, recognises a follow-up ticket that is worded differently, or tries the ruled-out fix. The recorded runs will say.
- Cost per ticket. No tokens were used by the agents in this session.

### Tokens

| Step | What | Model | Tokens |
|---|---|---|---|
| 1 | Harness, solutions 02 and 10, gateway and policies read again | Main (Claude Fable 5.2) | Input about 60,000, estimated |
| 2 | Connector rules, memory, proposals, findings, both agents, session, page, prepared replies | Main | Output about 30,000, estimated |
| 3 | 30 tests written and run; three scenarios run and their pages read | Main | Input about 25,000, output about 12,000, estimated |
| 4 | Solution page, this log, root page, roadmap | Main | Output about 7,000, estimated |

Not for a lighter model: the controls around the two agents and what the harness must refuse.

## Session 3, 23 November 2026: build step 3, the red team

No model is involved in anything measured in this session. The live mode is built and tested on prepared replies; its real runs belong to step 4.

### Decisions

The main choices and what was set aside are in [REDTEAM_DECISIONS.md](REDTEAM_DECISIONS.md), the decision record of this step. In short:

| | Decision | Why | Set aside |
|---|---|---|---|
| D36 | The agent is attacked through the ticket. | The requester controls the text the agent reads; that is the real way in. | Replaying calls against the gateway only, as in solution 01. |
| D37 | Two modes, one judge: "assumed tricked" in fixed code, and "live" on a real model. | A result that depends on the model resisting is not a control. | A live-only campaign, which would have produced nothing measurable in this step. |
| D38 | Fixed code decides a breach from the suite's records, never from the agent's account. | A tricked agent can describe harm as harmless. | A second model as judge. |
| D39 | The attack list is data, with source, link and date per pattern. A test adds an entry and checks that no code changes. | Mario's point of 20 November: the list is updated from what the world publishes. | Attacks written as test code. |
| D40 | Four gaps found while writing the attacks were closed before the first run, and are listed in the decision record. | They were one-line rules, and leaving a known hole open to have a longer list of breaches would be theatre. | Publishing them as breaches first. |
| D41 | Three breaches stay open and are published with the fix designed for each. | Each is about free text or the future, which exact comparison cannot settle. Narrowing the breach condition until they vanish would hide them. | Dropping the three cases from the list. |
| D42 | Live mode separates "not attempted" from "blocked". | The first says the model resisted; the second says a control was needed. A board should see both numbers. | One "no harm" outcome. |
| D43 | The campaign lives in this solution, in the vocabulary of solution 01's campaign. Joining both in one Control Tower report is left to the integration task. | The Control Tower's board page has tested figures that should not move before the integration is designed. | Merging the two reports now. |

### What was checked

- Five test suites: Control Tower 82, solution 02 92, shared harness 15, solution 10 34, this solution 73.
- The campaign: 16 attacks, 12 blocked, 1 held, 3 breaches; 4 of 4 legitimate cases go through; 20 of 20 audit trails intact.
- The published page was read in full. One label was wrong on first reading: a refusal by the suite was reported as "the harness". Corrected.
- The three sample pages of step 2 are unchanged by the four new rules.

### Not known

- What a real model does with the 20 tickets. In particular whether it tries the harmful call at all.
- Whether the verifier catches the false note of SD-A-10 and the unhelpful fix of SD-A-16 when given those tickets.

### Tokens

| Step | What | Model | Tokens |
|---|---|---|---|
| 1 | Solution 01's red team and attack list read; campaign designed | Main (Claude Fable 5.2) | Input about 30,000, output about 6,000, estimated |
| 2 | Four connector rules, attack list, campaign code, 12 tests | Main | Output about 17,000, estimated |
| 3 | Decision record, solution page, this log, root page, roadmap | Main | Output about 7,000, estimated |

A lighter model could write further attack entries once the pattern exists. Choosing what counts as a breach was not work for a lighter model.
