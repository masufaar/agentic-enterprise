# Decision record: attacking our own service desk agent

23 November 2026. Why this record exists: until now the red team of this repository replayed harmful calls against the Control Tower's gateway. Here it attacks an agent through the thing the agent reads, the ticket. That is new ground in this repository, so the choices are written down with what was set aside.

## 1. What is attacked, and through what

**Decided:** the resolution agent, through the ticket. Each attack is a ticket text, taken from a published pattern, placed in a fresh copy of the synthetic service desk.

**Why:** that is how a service desk agent is reached in practice. The requester, or whoever writes to the service desk, controls the text the agent reads. Nobody needs access to the agent itself.

**Set aside:** attacks on the model provider, on the harness code and on the Control Tower's gateway. The gateway has its own campaign in [solution 01](../01-ai-governance-control-tower/reports/redteam-latest.md). The verifier is not attacked in this step; it reads the same hostile text and should be next.

## 2. Two ways to run the same attack

**Decided:** every case runs in two modes, judged by the same fixed code.

- **Assumed tricked.** No model. The agent is taken as fully compromised and makes exactly the calls the attacker wants, through its own tools. This answers: do the controls hold when the model does not?
- **Live.** The ticket is given to the agent on a real model, as an ordinary ticket. This answers: what does the model do? It needs a key and produces recorded runs.

**Why both:** a result that depends on the model resisting is not a control. Models change, and a ticket that fails today may work on the next version. The board should hear first what holds without the model's good sense, and second how often that good sense was needed.

**Set aside:** a second model writing new attacks during the run. It would make the campaign different every time, and a result that cannot be repeated cannot be compared between two versions of the agent. A model may later propose new entries for the list; a person adds them.

## 3. What counts as a breach

**Decided:** fixed code decides from the suite's own records: the ticket's state, the action taken, the notes written, where it was handed, the case memory, the proposals. Never from the agent's account of itself.

**Why:** an agent that was talked into a harmful act can also be talked into describing it as harmless. The solution's own principle, the record says what was done, applies to its red team.

**Outcomes:** blocked, held (waits for a named person), BREACH, and for the live mode "not attempted". Four legitimate cases must still go through, so the campaign cannot be passed by refusing everything.

## 4. Where the attacks come from

**Decided:** three attacks, each tied to a published incident or vulnerability with its date and link, in `data/attacks.json`. A newly published attack is a new entry in that file. A test adds one and checks that no code changes.

| Attack | Published pattern | Cases |
|---|---|---|
| The requester who is not the owner | Meta's AI support assistant, 20,225 accounts, reported 1 June 2026 | 6 |
| The ticket that carries hidden orders | CVE-2026-18883, 19 November 2026 | 7 |
| Pressure to close what is not solved | Resolution as the billing unit, TechTarget, 26 August 2026 | 3 |

**Limit, stated:** a new entry needs no code only while the existing ways of recognising harm are enough (eleven of them, such as "the ticket was closed" or "the note contains"). An attack that does a new kind of harm needs a new one.

## 5. What was found before the first published run

Writing each attack as the calls a compromised agent would make showed four gaps. They were closed before the campaign was first run, so they do not appear as breaches. They are listed here because they were real:

| Gap | Closed by |
|---|---|
| The suite offers "closed after 72 hours without a reply" as a resolution, and our agent could use it | The connector refuses an agent any entry that closes a ticket without fixing anything |
| A ticket could be handed over to any destination, including an address given in the ticket | Hand-over only to a team named in the briefing |
| The agent could copy other people's employee numbers from similar tickets into a note the requester reads | A note names nobody but the requester and what the ticket is about |
| The agent could read any ticket in full by number | Only a ticket that its own search or a case returned in that run |

## 6. What is published

**Decided:** everything, on every run: [reports/redteam-latest.md](reports/redteam-latest.md). Three breaches are open and published with the fix designed for each. None is hidden by narrowing the breach condition.

**Why these three stay open:** each is about free text or about the future. Whether a note is true, whether a lesson is honest and whether a fix will hold cannot be settled by comparing values. They are met by detection (the verifier), by keeping free text away from rules (no rule reads the memory), and by designed fixes, not by a claim that they are closed.

## 7. What this campaign does not show

- What a real model does. No live run is recorded yet.
- Attacks on the verifier, or on both agents together.
- An owner who is tricked into confirming a second-factor prompt. In the stand-in the owner confirms only their own request.
- Attacks spread over several tickets, where each ticket is harmless on its own.
- Anything about a real service desk suite. The suite is a stand-in.
