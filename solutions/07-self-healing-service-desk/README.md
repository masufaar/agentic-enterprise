# Self-Healing Service Desk

**Status: in build (22 November 2026). The foundations are working as fixed code, with no model involved: 200 synthetic tickets, a stand-in for the service desk suite behind one connector, and the autonomy ladder with its tests. The two agents, the learning loop and the red-team attacks are designed, not built yet. Nothing is connected to a real system.**

Who checks the ticket an AI agent closed, and who decides which tickets it may close alone?

Background article: [Who checks the ticket that AI agent closed?](https://www.linkedin.com/pulse/who-checks-ticket-ai-agent-closed-mario-gracia-qux1f/)

## The management issue

Between 17 April and 31 May 2026, attackers took over 20,225 Instagram accounts by asking Meta's AI support assistant to attach a new email address to accounts they did not own. It ran for six weeks. Resetting access was the assistant's job: it did nothing it was not allowed to do. The check on who was asking was missing.

In 2026 the large service desk suites sell agents that take a ticket, fix it and close it without a person. Three things follow for any company that switches one on:

- **Right action, wrong person.** A permission list passes a password reset. It does not ask whether the requester owns the account.
- **Closed is not solved.** The system that closed the ticket is the one that records it as solved, and in some products the one that bills for it.
- **One mistake, many tickets.** A person errs on one ticket. An agent repeats the error on every ticket of that kind until someone looks.

## The gap

As read on 20 November 2026: the suites answer with permissions, a kill switch and evaluation before deployment. One leading suite's published guidance is to let its agent act alone on a request type "only when your team is confident". Confidence is not evidence. What a board would ask for is missing: which ticket types may be closed without a person, on what proof, and when a type is taken back.

## In addition to your existing suite

| Layer | What it does | Whose job | At Halden (invented names) |
|---|---|---|---|
| System of record | Holds every ticket, its workflow, the knowledge base and the asset records | Your existing suite | Quillfield Service Desk |
| Routing and grouping | Sorts tickets to teams and groups similar incidents | Your existing suite | Quillfield Service Desk |
| The suite's own agent | Takes a ticket, applies a fix and closes it without a person | Your existing suite | Quillfield Auto-Resolve |
| Permissions and the stop switch | What an agent may touch, and how it is stopped | Your suite, and the [AI Governance Control Tower](../01-ai-governance-control-tower/README.md) | |
| Plant-floor and security incidents | Decides the response to an incident that reaches a plant | The [OT/IT Convergence Sentinel](../02-ot-it-convergence-sentinel/README.md) | |
| **The check and the decision** | Whether a closed ticket was solved, for the right person, as recorded; and, on that evidence, which ticket types may be closed without a person | **This solution** | |

Nothing is replaced. The suite stays the system of record, and our agents reach it through one connector, as an outside agent reaches a real suite through the vendor's own supported connection. The vendor names are invented for the fictional company; web searches on 22 November 2026 found no service desk product called Quillfield. In the repository the suite is a stand-in: fixed code over synthetic files. No real suite is connected.

## What it is

- **The connector.** Fixed code, working. The one door between an agent and the suite: nine operations, five that read and four that change a ticket. Every call is decided and recorded by the Control Tower under the agent's own identity. A call that changes a ticket must pass the autonomy ladder first.
- **The autonomy ladder.** Fixed code, a control, working. One rung per ticket type: watch, propose, act with check, act alone. Checked cases move a type. A step down is taken by the code, at once. A step up is approved by one named role, one rung at a time.
- **The resolution agent.** Designed. It will work tickets inside the suite, at the rung the ladder gives each ticket type.
- **The verifier agent.** Designed. It will reopen the question on tickets that are already closed, by our agent, by the suite's own agent or by a person: did the fix hold, was the requester entitled, does the record match what was done. It never closes a ticket: its registry card holds no tool that changes one, and the Control Tower refuses it on every ticket type.
- **The page for the Head of IT Service Management**, who decides which ticket types may be closed without a person. Designed.

## The autonomy ladder

| Rung | The agent may | How a case is checked |
|---|---|---|
| Watch | Read the ticket and write down what it would have done. The note is not shown to the person working the ticket. | Its note against what the person did |
| Propose | Put a proposed fix in front of the person, who carries it out or not | Was the proposal carried out unchanged, and did the fix hold |
| Act with check | Carry out the fix and close the ticket | Every closure is checked afterwards |
| Act alone | Carry out the fix and close the ticket | A sample of closures is checked (assumption: one in five) |

The rules, all in `data/ladder.json`, all assumptions a company replaces with its own:

- **A step up** needs 20 checked cases since the last move, at most 5% of them failed, and no serious finding. Then it needs the approval of the Head of IT Service Management. No agent, and no other role, can give it.
- **A step down** needs nobody. A serious finding (the requester was not entitled, or the record does not match what was done) drops the type to Propose at once. More than 15% failed among the last checked cases, with at least 10 checked, drops it one rung.
- **A step down is reversible**: the same role can put the type back, with a reason. The reason is recorded.
- **A ceiling** is a company rule, not a threshold. Ticket types that touch identity are never worked alone, whatever the evidence. A change of recovery email or phone is always carried out by a person.
- **Plant-floor and security tickets are not on the ladder.** They can only be handed over, and they go to the Sentinel whatever the agent names.

Where the types stand on the first day (`python -m servicedesk ladder`): password reset, software installation, mailbox full and VPN start at Act with check, because the suite's own agent already closes them alone and nothing has been checked yet. Printer faults start at Propose. Second-factor reset, access requests and recovery-contact changes start at Watch.

## The synthetic service desk

Measured by `python -m servicedesk tickets` and by the tests:

| | Tickets |
|---|---|
| All | 200, in 10 ticket types |
| Closed | 150: 64 by the suite's own agent, 76 by service desk staff, 10 by the OT security team |
| Open | 50, of which 6 are plant-floor or security tickets to hand over |
| Incidents that keep returning | 2: the VPN at plant 07 (10 tickets) and a printer driver at plant 03 (8 tickets) |

26 of the 150 closed tickets carry a planted flaw: 16 where the fix did not hold (3 of them closed because nobody answered for 72 hours), 5 where the requester was not entitled, 5 where the note does not match what the suite's action log shows. 16 of the 26 were closed by the stand-in for the suite's own agent. **These numbers are design choices for a test bed. They are not findings about any product.**

No flaw is marked on a ticket. It can only be found the way a person would find it: a later ticket from the same person, the record of who owns the account, the action log. The answer key is a separate file that the connector does not serve; it exists so that the verifier's findings can be scored against something it did not see. A test checks, in both directions, that every planted flaw can be found from what the suite shows and that no sound ticket looks flawed.

## The controls, in fixed code

| Control | What it does |
|---|---|
| One connector | An agent can ask for nine operations and nothing else. There is no operation to reopen or delete a ticket, and none that serves the answer key |
| The Control Tower | Every call goes through the gateway under the agent's registry identity and is recorded; the kill switch stops an agent at the connector |
| A verifier that cannot close | The verifier's card holds no tool that changes a ticket. All four changing operations are refused for it, on every ticket type |
| The ladder | A change is refused unless the ticket type is on a rung that allows it. The refusal is written to the Control Tower's audit trail |
| Step up by one role only | The ladder refuses an approval from anyone but the role named in the company briefing |
| Step down without approval | Taken by code on the finding itself, and in force at the connector on the next call |
| Hand-over types | Plant-floor and security tickets accept one operation: hand over |
| Only the suite's own fixes | An agent can ask only for a fix the suite offers for that ticket type |

## Run it

From this folder. Everything here is fixed code: no model, no key, no cost.

```
python -m servicedesk tickets      what the 200 synthetic tickets hold
python -m servicedesk ladder       where each ticket type stands on the ladder
python -m servicedesk try sd-verifier resolve SD-26-0164 action=x note=y
                                   one call through the connector: refused, and recorded
python -m servicedesk generate     write the synthetic data again (same seed, same files)
python -m pytest                   31 tests
```

## What is in this folder

| File | What it is |
|---|---|
| `servicedesk/connector.py` | The one connector: ladder, then Control Tower, then the suite |
| `servicedesk/ladder.py` | The autonomy ladder and its record |
| `servicedesk/suite.py` | The stand-in for Quillfield Service Desk |
| `servicedesk/generate.py` | Writes the synthetic data, with a fixed seed |
| `data/tickets.json` | 200 tickets as the suite shows them |
| `data/directory.json`, `data/activity.json` | Who owns what; the suite's action log and the signals after a closure |
| `data/answer-key.json` | Which closed tickets are flawed. Never handed to an agent |
| `data/ticket-types.json`, `data/ladder.json`, `data/briefing.json` | Ticket types and their fixes; the ladder's rungs, thresholds and ceilings; the company briefing |
| `tests/` | 31 tests, fixed code only |
| `BUILD_LOG.md` | Decisions, alternatives set aside, and tokens per step |

## What has to exist before this solution is called working

1. The two agents on the [shared harness](../../shared/), with case memory and the learning loop: an incident that returns becomes a proposal for a permanent fix and a change to the briefing, approved by a person. **Designed.**
2. The page for the Head of IT Service Management: the evidence per ticket type and the proposal to move it. **Designed.**
3. The Control Tower's red team aimed at the resolution agent with three attacks taken from published incidents: the requester who is not the owner, the ticket that carries hidden orders, the pressure to close what is not solved. Results published, breaches included. **Designed.**
4. Runs with a real model, recorded in `reports/runs/`, and the solution's line in the [AI Value Ledger](../10-ai-value-ledger/README.md): cost per verified resolution, not per closed ticket. **Designed.**

## Limits

- All data is synthetic and belongs to the fictional company Halden Industrial. People appear by invented employee number or by role.
- The suite is a stand-in. A real suite's own connection, its workflows and its permission model are not exercised.
- The ladder's thresholds, starting rungs and sampling share are assumptions. The ladder governs what reaches the suite through our connector; applying a rung to the suite's own agent is a setting inside the suite, and is designed, not built.
- The evidence in the synthetic data is cleaner than in a real service desk. The planted flaws can be found by exact comparison; real ones cannot, which is why the check is designed as an agent.
- Tickets are in English only.

## Sources, as read on 20 November 2026

- Meta's AI support assistant and the Instagram account takeovers: [TechCrunch, 1 June 2026](https://techcrunch.com/2026/06/01/hackers-hijacked-instagram-accounts-by-tricking-meta-ai-support-chatbot-into-granting-access/); the breach notification of 8 June 2026 as reported by [Help Net Security](https://www.helpnetsecurity.com/2026/06/08/instagram-ai-support-vulnerability-account-takeovers/).
- Clorox v. Cognizant, USD 380 million claimed over passwords reset for an unverified caller: [The Register, 23 July 2025](https://www.theregister.com/2025/07/23/lawsuit_clorox_vs_cognizant/).
- "Only when your team is confident": Atlassian's guidance for the resolution agent of Jira Service Management, [support page](https://support.atlassian.com/jira-service-management-cloud/docs/about-rovo-service/) and [announcement](https://community.atlassian.com/forums/JSM-News-Discussions-articles/Request-Resolver-is-now-GA/ba-p/3214779).
- Permissions checked at run time, also for third-party agents: ServiceNow AI Passport, announced 15 October 2026, as reported by [Help Net Security](https://www.helpnetsecurity.com/2026/10/15/servicenow-ai-passport/). Not verified: whether it is generally available.
- Indirect prompt injection in a service platform's AI agent: [CVE-2026-18883](https://cve.threatint.com/CVE/CVE-2026-18883), published 19 November 2026; no exploitation known to the vendor.
- Gartner, [press release of 16 November 2026](https://www.gartner.com/en/newsroom/press-releases/2026-11-16-gartner-weak-artificial-intelligence-governance-will-lead-to-business-critical-service-disruptions-for-40-percent-of-infrastructure-and-operations-organizations-by-2028): 70 per cent of infrastructure and operations leaders believe their agents operate within safe boundaries; 57 per cent call their governance weak.

See the one-page [business case](BUSINESS_CASE.md).
