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
