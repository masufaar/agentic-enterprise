# Self-Healing Service Desk

**Status: in build (22 November 2026). Working as fixed code, with no model involved: 200 synthetic tickets, a stand-in for the service desk suite behind one connector, the autonomy ladder, the case memory, the page. The two agents are in build: the resolution agent and the verifier are built on the shared harness and tested on prepared replies; no run with a real model is recorded yet, so nothing is claimed about what a model does with them. The red-team attacks are designed. Nothing is connected to a real system.**

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

- **The connector.** Fixed code, working. The one door between an agent and the suite: ten operations, five that read and five that change a ticket. Every call is decided and recorded by the Control Tower under the agent's own identity. A call that changes a ticket must pass the autonomy ladder first.
- **The autonomy ladder.** Fixed code, a control, working. One rung per ticket type: watch, propose, act with check, act alone. Checked cases move a type. A step down is taken by the code, at once. A step up is approved by one named role, one rung at a time.
- **The resolution agent.** In build. It works one open ticket at a time inside the suite, at the rung the ladder gives the ticket type. A refused step is handed back to it with the reason, and it decides what is still right for the person who asked.
- **The verifier agent.** In build. It reopens the question on a ticket that is already closed, by our agent, by the suite's own agent or by a person: did the fix hold, was the requester entitled, does the record match what was done. It never closes a ticket: it is given no tool that changes one, its registry card holds none, and the Control Tower refuses it on every ticket type.
- **The page for the Head of IT Service Management**, who decides which ticket types may be closed without a person. Fixed code, working: see the three [sample pages](reports/samples/), made with prepared replies in place of a model.

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

## The two agents

Both run in the [shared harness](../../shared/): a language model in a loop, asking for tools that are fixed code, finished only when the harness accepts its hand-in. **Status: in build. Everything below is tested on prepared replies; what a real model does with it is shown only by recorded runs, which do not exist yet.**

| | Resolution agent (`sd-resolution`) | Verifier agent (`sd-verifier`) |
|---|---|---|
| Its job | Work one open ticket | Check one closed ticket |
| It reads | The ticket and its rung, the owner's record, similar tickets, earlier cases | The ticket, the owner's record, the action log, later tickets, earlier cases |
| It can change | The ticket of its run only: note, proposed fix, fix and closure, hand-over, a second-factor prompt to the owner | Nothing in the suite. It files a finding in the company's own record |
| It hands in | What it did, why, and one sentence for the next ticket | Three answers (yes, no, cannot tell), the evidence, and one sentence for the next case |

What the harness refuses, whatever the model writes:

| Control | What it does |
|---|---|
| Who is asking | A fix on a ticket type that touches identity is carried out only when the suite itself has confirmed the requester as the owner of the account. What the ticket says does not count |
| Say what was done | The agent's hand-in must name the last step the suite recorded. A ticket is not resolved because the agent says so |
| One ticket per run | The tools that change a ticket take no ticket number: they act on the ticket of the run |
| Read before you judge | A finding is accepted only after the owner's record, the action log and the later tickets have been read in that run |
| Evidence that exists | "The fix did not hold" must name a later ticket a tool returned. Every ticket named must be one the agent has read |
| Not too early | "The fix held" is not accepted before the seven follow-up days are over. Until then the answer is "cannot tell", and the ticket is listed to be checked again |
| The verifier does not rule | What a finding means for the ladder is worked out by fixed code: a requester who was not entitled, or a record that does not match, is serious |
| Word limits | Every text stays within the limits of the company briefing |

## The learning loop

- **Case memory.** After each ticket, fixed code keeps the facts and the agent's one-sentence lesson. Before the next ticket, either agent can read the earlier cases that share a device, an account, a group of incidents or a site with it. Reading and writing go through the Control Tower.
- **The same incident is not solved twice.** When an incident keeps coming back, the resolution agent can propose a permanent fix and a standing instruction for the company briefing. It needs at least two tickets the agent has read. The Control Tower holds the text for a named person (rule P-011) and refuses it if it carries personal data (rule P-010).
- **Approved by a person, then enforced.** Nothing changes until the Head of IT Service Management approves. Then the instruction is part of the briefing in force: both agents read it, and the connector refuses the fix it rules out for that incident. The briefing file itself is never rewritten by an agent.

## Three scenarios

| Scenario | What happens | What it shows |
|---|---|---|
| `sound-batch` | Three closures by the suite's own agent are checked; our agent closes a full mailbox; that closure is checked too | A sound batch counts on the ladder. Our own closure is checked like any other, and is too fresh to count |
| `wrong-requester` | Our agent closes a password reset. Three resets closed by the suite's own agent are checked; two were for someone who was not the owner. The next reset and the owner's own ticket follow | The type drops to Propose at once. The same kind of ticket is closed before the findings and only proposed after them, with the reason on the page |
| `incident-returns` | Two closures of the VPN fault at plant 07 are checked; our agent works the next one, proposes a permanent fix; the approval is given; the next ticket follows | One case changes the next. An approved instruction changes what the agents do, with no change to code |

In `incident-returns` the approval is given by the scenario file, standing in for the Head of IT Service Management, and the page says so.

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
| One connector | An agent can ask for ten operations and nothing else. There is no operation to reopen or delete a ticket, and none that serves the answer key |
| The Control Tower | Every call goes through the gateway under the agent's registry identity and is recorded; the kill switch stops an agent at the connector |
| A verifier that cannot close | The verifier's card holds no tool that changes a ticket. All four changing operations are refused for it, on every ticket type |
| The ladder | A change is refused unless the ticket type is on a rung that allows it. The refusal is written to the Control Tower's audit trail |
| Step up by one role only | The ladder refuses an approval from anyone but the role named in the company briefing |
| Step down without approval | Taken by code on the finding itself, and in force at the connector on the next call |
| Hand-over types | Plant-floor and security tickets accept one operation: hand over |
| Only the suite's own fixes | An agent can ask only for a fix the suite offers for that ticket type |

## Run it

From this folder. These commands are fixed code: no model, no key, no cost.

```
python -m servicedesk tickets      what the 200 synthetic tickets hold
python -m servicedesk ladder       where each ticket type stands on the ladder
python -m servicedesk try sd-verifier resolve SD-26-0164 action=x note=y
                                   one call through the connector: refused, and recorded
python -m servicedesk generate     write the synthetic data again (same seed, same files)
python -m servicedesk sample       the three scenarios with prepared replies in place of a model;
                                   writes the sample pages in reports/samples
python -m pytest                   61 tests
```

With a real model. It needs the environment variable `HALDEN_MODEL_KEY_FILE`, the path of a file that holds the model key; the key is read at the moment of the call and is never logged or stored.

```
python -m servicedesk scenarios
python -m servicedesk run wrong-requester --record     one scenario; writes the page and keeps the run
python -m servicedesk runs --record                    all three
```

## What is in this folder

| File | What it is |
|---|---|
| `servicedesk/connector.py` | The one connector: ladder, then Control Tower, then the suite |
| `servicedesk/ladder.py` | The autonomy ladder and its record |
| `servicedesk/suite.py` | The stand-in for Quillfield Service Desk |
| `servicedesk/generate.py` | Writes the synthetic data, with a fixed seed |
| `servicedesk/resolution.py`, `servicedesk/verifier.py` | The two agents: what each is told, its tools, and what the harness checks before it accepts a hand-in |
| `servicedesk/findings.py` | The company's own record of what was checked, and what a finding means for the ladder |
| `servicedesk/memory.py`, `servicedesk/proposals.py` | Case memory; proposals for a permanent fix and their approval |
| `servicedesk/session.py`, `servicedesk/page.py` | A scenario from its steps to the page for the Head of IT Service Management |
| `servicedesk/prepared.py` | Prepared replies for the tests and the sample pages. Not a model |
| `data/scenarios/` | The three scenarios |
| `reports/samples/` | The three pages as fixed code writes them, with prepared replies |
| `data/tickets.json` | 200 tickets as the suite shows them |
| `data/directory.json`, `data/activity.json` | Who owns what; the suite's action log and the signals after a closure |
| `data/answer-key.json` | Which closed tickets are flawed. Never handed to an agent |
| `data/ticket-types.json`, `data/ladder.json`, `data/briefing.json` | Ticket types and their fixes; the ladder's rungs, thresholds and ceilings; the company briefing |
| `tests/` | 61 tests: 31 on the foundations, 30 on the agents' controls with prepared replies |
| `BUILD_LOG.md` | Decisions, alternatives set aside, and tokens per step |

## What has to exist before this solution is called working

1. Runs with a real model on the three scenarios, recorded in `reports/runs/`, with the verifier's findings compared with the answer key. **Next.** Until then the two agents are in build.
2. The Control Tower's red team aimed at the resolution agent with three attacks taken from published incidents: the requester who is not the owner, the ticket that carries hidden orders, the pressure to close what is not solved. Results published, breaches included. **Designed.** The controls those attacks will meet (who is asking, say what was done, hand-over types) are built and tested; whether a model holds under attack is not known.
3. The solution's line in the [AI Value Ledger](../10-ai-value-ledger/README.md): cost per verified resolution, not per closed ticket. **Designed.**

## Limits

- All data is synthetic and belongs to the fictional company Halden Industrial. People appear by invented employee number or by role.
- The suite is a stand-in. A real suite's own connection, its workflows and its permission model are not exercised.
- The ladder's thresholds, starting rungs and sampling share are assumptions. The ladder governs what reaches the suite through our connector; applying a rung to the suite's own agent is a setting inside the suite, and is designed, not built.
- The evidence in the synthetic data is cleaner than in a real service desk. The planted flaws can be found by exact comparison; real ones cannot, which is why the check is designed as an agent.
- Tickets are in English only.
- In a scenario, a decision of the Head of IT Service Management is given by the scenario file. There is no screen for that role yet; the page is a file.
- A second-factor prompt in the stand-in is confirmed when the requester is the owner and never otherwise. A real owner can also be tricked into confirming; that is not modelled.
- The verifier's finding on whether a fix held rests on a later ticket. A person who gives up and never writes again looks like a held fix.

## Sources, as read on 20 November 2026

- Meta's AI support assistant and the Instagram account takeovers: [TechCrunch, 1 June 2026](https://techcrunch.com/2026/06/01/hackers-hijacked-instagram-accounts-by-tricking-meta-ai-support-chatbot-into-granting-access/); the breach notification of 8 June 2026 as reported by [Help Net Security](https://www.helpnetsecurity.com/2026/06/08/instagram-ai-support-vulnerability-account-takeovers/).
- Clorox v. Cognizant, USD 380 million claimed over passwords reset for an unverified caller: [The Register, 23 July 2025](https://www.theregister.com/2025/07/23/lawsuit_clorox_vs_cognizant/).
- "Only when your team is confident": Atlassian's guidance for the resolution agent of Jira Service Management, [support page](https://support.atlassian.com/jira-service-management-cloud/docs/about-rovo-service/) and [announcement](https://community.atlassian.com/forums/JSM-News-Discussions-articles/Request-Resolver-is-now-GA/ba-p/3214779).
- Permissions checked at run time, also for third-party agents: ServiceNow AI Passport, announced 15 October 2026, as reported by [Help Net Security](https://www.helpnetsecurity.com/2026/10/15/servicenow-ai-passport/). Not verified: whether it is generally available.
- Indirect prompt injection in a service platform's AI agent: [CVE-2026-18883](https://cve.threatint.com/CVE/CVE-2026-18883), published 19 November 2026; no exploitation known to the vendor.
- Gartner, [press release of 16 November 2026](https://www.gartner.com/en/newsroom/press-releases/2026-11-16-gartner-weak-artificial-intelligence-governance-will-lead-to-business-critical-service-disruptions-for-40-percent-of-infrastructure-and-operations-organizations-by-2028): 70 per cent of infrastructure and operations leaders believe their agents operate within safe boundaries; 57 per cent call their governance weak.

See the one-page [business case](BUSINESS_CASE.md).
