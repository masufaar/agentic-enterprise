# Supply chain disruption: what does this event do to us, and who signs off?

For the Head of Supply Chain. Session: A single-source halt (Nordkamp, PCM-7). Systems as of 2026-02-13. All data is synthetic (Halden Industrial). The risk feed (Larkspur Supply Signals) and the ERP (Fenmark MRP) are stand-ins under invented vendor names; no real system is connected.

**This page was produced with prepared replies in place of a model. It shows the fixed code around the agents working; it proves nothing about a model.**

**The question:** Which products, orders and cash does the Nordkamp halt touch, and what do we do before cover runs out?

## What needs your decision

- **Sign-off, for you:** purchase_order to SUP-TORNA, EUR 21,000. Drafted, not sent.
- **Sign-off, for you:** email to orders@tornelis.example. Drafted, not sent.

## The exposure, mapped onto the bill of materials

| Event | Material | Kind | Parts | Products | Revenue at risk | Cover (days) | Confidence |
|---|---|---|---|---|---|---|---|
| EV-01 | yes | stoppage | PCM-7 | PRD-A, PRD-B, PRD-C, PRD-F | EUR 1,143,000 | 12 | high |

**EV-01** (Nordkamp halts shipments amid ownership dispute), the monitor's assessment:
> Nordkamp has halted shipments of the single-source part PCM-7. It feeds four products with EUR 1,143,000 of open orders, and cover is only 12 days, inside the 21-day buffer.
What it keeps for the next event:
> A halt at the single source of PCM-7 cascades to four products; 12 days of cover is the clock.

## What the sourcing agent proposed

**Event EV-01**, the sourcing agent's recommendation:
> Ranked: 1) qualified PO to Tornelis (held for sign-off), the only qualified second source; 2) an email to Tornelis to pull the lead time in; 3) recommend the Head of Supply Chain re-allocate PCM-7 stock to the two highest-revenue orders. Do not use the unqualified supplier.
Options it weighed:
- Qualified PO to Tornelis, EUR 21,000, lead 70 days (held)
- Supplier email to Tornelis to shorten lead (held)
- Re-allocate stock to CO-001 and CO-003 (recommended; a person decides)
Drafts held for the Head of Supply Chain: purchase_order to SUP-TORNA; email to orders@tornelis.example.
What it keeps for the next event:
> The qualified second source is slower and dearer, but it is the only one an agent may draft.

## The autonomy ladder after this session

| Action type | Rung | Ceiling | Sound cases since last move | Not sound | Serious | Step up |
|---|---|---|---|---|---|---|
| supplier_email | Propose | Act with check | 0 | 0 | 0 | 0 of 5 sound cases since the last move. |
| expedite | Propose | Act with check | 0 | 0 | 0 | 0 of 5 sound cases since the last move. |
| new_po_qualified | Propose | Act with check | 1 | 0 | 0 | 1 of 5 sound cases since the last move. |
| new_po_unqualified | Watch | Watch | 0 | 0 | 0 | At its ceiling (Watch): a company rule, not a threshold. |

## Decisions taken in this session

- Recorded an ok case for action type 'new_po_qualified' (EV-01). Given by the scenario file, standing in for the Head of Supply Chain. One sound case. Four more, clean, and the Head of Supply Chain is offered a step up.

## What was held for you, drafted and not sent

| Draft | Part | Supplier / to | Amount | Action type | Held for |
|---|---|---|---|---|---|
| purchase_order | PCM-7 | SUP-TORNA | EUR 21,000 | new_po_qualified | Head of Supply Chain |
| email | — | orders@tornelis.example | — | supplier_email | Head of Supply Chain |

## What was refused or held

| Agent | Step | Stopped or held by | Reason | Times |
|---|---|---|---|---|
| sourcing-options | draft_po | Control Tower rule P-005,P-009 | held for a person: Purchase orders above EUR 10,000 need a named human approver (assumption). | 1 |
| sourcing-options | draft_supplier_email | Control Tower rule P-006,P-009 | held for a person: Email to an address outside the company needs a named human approver. | 1 |

## How this page was made

- disruption-monitor: scripted stand-in (no model); sourcing-options: scripted stand-in (no model).
- Agent turns: disruption-monitor 5 (handed in), sourcing-options 5 (handed in).
- Tokens: 0 in, 0 out. 0.0 seconds from the first step to this page.
- The Control Tower recorded 7 steps for this session; chain intact.
- Checked afterwards against the answer key, which no agent was shown: 1 of 1 assessments agree on whether the event was material and which products it hit.
- Hand-ins the harness did not accept and handed back for correction: 1.
- The monitor has no tool that moves money or supply. Every purchase order and every email is held for the Head of Supply Chain. A step up on the ladder is never taken by an agent.
