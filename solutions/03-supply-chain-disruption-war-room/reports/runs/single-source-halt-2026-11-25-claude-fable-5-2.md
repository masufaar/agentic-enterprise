# Supply chain disruption: what does this event do to us, and who signs off?

For the Head of Supply Chain. Session: A single-source halt (Nordkamp, PCM-7). Systems as of 2026-02-13. All data is synthetic (Halden Industrial). The risk feed (Larkspur Supply Signals) and the ERP (Fenmark MRP) are stand-ins under invented vendor names; no real system is connected.

**The question:** Which products, orders and cash does the Nordkamp halt touch, and what do we do before cover runs out?

## What needs your decision

- **Sign-off, for you:** email to SUP-NORD. Drafted, not sent.
- **Sign-off, for you:** email to SUP-TORNA. Drafted, not sent.

## The exposure, mapped onto the bill of materials

| Event | Material | Kind | Parts | Products | Revenue at risk | Cover (days) | Confidence |
|---|---|---|---|---|---|---|---|
| EV-01 | yes | stoppage | PCM-7 | PRD-A, PRD-B, PRD-C, PRD-F | EUR 1,143,000 | 12 | high |

**EV-01** (Nordkamp halts shipments amid ownership dispute), the monitor's assessment:
> Verified halt at Nordkamp (SUP-NORD), sole source of PCM-7, a single-source power control module. Cover is 12 days against the 21-day buffer; supplier lead time is 56 days. Trace shows four products (PRD-A, PRD-B, PRD-C, PRD-F) and six open orders (CO-001, -002, -003, -004, -007, -008), EUR 1,143,000 at risk. Not known: how long the halt lasts, any stock in transit, whether a qualified alternative exists. Any response needs the Head of Supply Chain.
What it keeps for the next event:
> A verified halt at a single-source supplier is a stoppage risk whenever cover is below the 21-day buffer; trace by supplier first and state halt duration as unknown.

## What the sourcing agent proposed

**Event EV-01**, the sourcing agent's recommendation:
> No option closes the gap: cover is 12 days, the only qualified alternate takes 70. Ranked: 1) Email Nordkamp for halt scope, in-transit stock and resume date (drafted, held for Head of Supply Chain sign-off; no cost). 2) Email Tornelis to confirm PCM-7 qualification, lead time and any early partial (drafted, held for sign-off; no cost). 3) PO to Tornelis, 8,400 units, about EUR 446,880, 70 days: NOT drafted, refused as above my spend limit (P-003); I did not split it. Head of Supply Chain to decide and raise. 4) Re-allocate the 4,800 on hand to committed orders: words only, Head's decision. Greywater is unqualified: excluded. No expedite drafted: no open order seen.
Options it weighed:
- Email Nordkamp (SUP-NORD): confirm halt scope, PCM-7 in transit, releasable stock, resume date. Cost nil; reply time unknown. Drafted, held for Head of Supply Chain.
- Email Tornelis (SUP-TORNA): confirm PCM-7 PPAP still current, real lead time, early partial shipment, capacity at 400/day. Cost nil. Drafted, held for Head of Supply Chain.
- PO to Tornelis, qualified second source: 8,400 units (21 days of consumption) at EUR 53.20 (38 x 1.4) = EUR 446,880, lead 70 days. Does not prevent a line stop from day 12; caps its length if the halt persists. NOT drafted: refused by control P-003 (above agent spend limit). Not split or resized to get under the limit. Needs the Head of Supply Chain to raise or authorise.
- Re-allocate the 4,800 units on hand (12 days at 400/day) toward the committed orders CO-001, -002, -003, -004, -007, -008 across PRD-A, -B, -C, -F, to stretch cover for the highest-priority commitments. Recommendation in words only; the split between customers and plants is the Head of Supply Chain's decision. Cost: deferred revenue on de-prioritised orders, not quantified.
- Expedite on an open Nordkamp order: not drafted. No open PO or in-transit quantity is visible to me, and the supplier has halted shipments; revisit once Nordkamp replies.
- Greywater Components (SUP-GREY): 30 days, price index 0.95, but not qualified (no PPAP, never audited). Rejected; not drafted. Even at 30 days it would not cover a 12-day gap.
- Not known: halt duration; stock in transit; open PO quantities with Nordkamp; whether Tornelis can ship early. ERP inconsistency: Tornelis's supplier record lists only CBL-3 and a 35-day lead, while the alternates list shows PCM-7 qualified at 70 days. Confirm before any PO is released.
Drafts held for the Head of Supply Chain: email to SUP-NORD; email to SUP-TORNA.
Refused on the way (Control Tower: over the spend limit): A purchase order may not exceed the agent's own spend limit.
What it keeps for the next event:
> For a single-source halt, compare alternate lead time to days of cover first; if the qualified PO exceeds the agent spend limit, hand it to the Head of Supply Chain in words rather than resizing it.

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
| email | — | SUP-NORD | — | supplier_email | Head of Supply Chain |
| email | — | SUP-TORNA | — | supplier_email | Head of Supply Chain |

## What was refused or held

| Agent | Step | Stopped or held by | Reason | Times |
|---|---|---|---|---|
| sourcing-options | draft_po | Control Tower: over the spend limit | A purchase order may not exceed the agent's own spend limit. | 1 |
| sourcing-options | draft_supplier_email | Control Tower rule P-006,P-009 | held for a person: Email to an address outside the company needs a named human approver. | 2 |

## How this page was made

- disruption-monitor: claude-fable-5-2, effort medium; sourcing-options: claude-fable-5-2, effort medium.
- Agent turns: disruption-monitor 2 (handed in), sourcing-options 4 (handed in).
- Tokens: 20,651 in, 4,062 out. 39.74 seconds from the first step to this page.
- The Control Tower recorded 14 steps for this session; chain intact.
- Checked afterwards against the answer key, which no agent was shown: 1 of 1 assessments agree on whether the event was material and which products it hit.
- Hand-ins the harness did not accept and handed back for correction: 0.
- The monitor has no tool that moves money or supply. Every purchase order and every email is held for the Head of Supply Chain. A step up on the ladder is never taken by an agent.
