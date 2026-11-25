# Supply chain disruption: what does this event do to us, and who signs off?

For the Head of Supply Chain. Session: A tariff on HSG-4 (a cost, not a stoppage). Systems as of 2026-02-13. All data is synthetic (Halden Industrial). The risk feed (Larkspur Supply Signals) and the ERP (Fenmark MRP) are stand-ins under invented vendor names; no real system is connected.

**The question:** A tariff raises the cost of a part used by four products. What is the exposure, and what is held for sign-off?

## What needs your decision

- **Sign-off, for you:** email to SUP-VALO. Drafted, not sent.

## The exposure, mapped onto the bill of materials

| Event | Material | Kind | Parts | Products | Revenue at risk | Cover (days) | Confidence |
|---|---|---|---|---|---|---|---|
| EV-02 | yes | cost | HSG-4 | PRD-A, PRD-C, PRD-D, PRD-F | EUR 1,116,000 | 50 | medium |

**EV-02** (25% tariff announced on imported aluminium housings), the monitor's assessment:
> Verified tariff on HSG-4, a multi-source, non-critical housing used in PRD-A, PRD-C, PRD-D and PRD-F. It is a cost event, not a supply interruption: cover is 50 days against the 21-day buffer. Five open orders (CO-001, 003, 004, 005, 007) worth EUR 1,116,000 use the part; that is the order value touched, not expected lost revenue. Not known: which import jurisdiction applies, whether SUP-VALO's shipments fall under it, and the actual landed-cost increase.
What it keeps for the next event:
> A verified tariff on a multi-source part with cover above buffer is a cost exposure, not a stoppage; report traced order value as touched, not lost, and state the unknown jurisdiction and cost impact.

## What the sourcing agent proposed

**Event EV-02**, the sourcing agent's recommendation:
> Cost event, not a stoppage: HSG-4 has 50 days of cover against a 21-day buffer. 1) Email to Valoria (SUP-VALO) asking whether the tariff applies and the landed-cost change: drafted, held for the Head of Supply Chain to sign off; no cost, reply asked within five working days. 2) If Valoria confirms an increase above about 10%, a PO to qualified Rheinwerk (SUP-RHEIN, 35 days, price index 1.1): not drafted; would need sign-off. 3) No expedite or re-allocation. Not known: jurisdiction, whether Valoria's shipments are in scope, actual cost. Rheinwerk's ERP record does not list HSG-4 and shows 28 days; confirm first.
Options it weighed:
- Supplier email to SUP-VALO (Valoria Metals) to confirm tariff scope, effective date and landed-cost change. Cost EUR 0; reply requested in five working days. Drafted and held for the Head of Supply Chain. Ranked 1.
- PO to qualified alternate SUP-RHEIN (Rheinwerk Components). Lead time 35 days, price index 1.1, i.e. about EUR 13.20 per unit against EUR 12; roughly EUR 264 a day extra at 220 units a day, against up to about EUR 660 a day if the full 25% landed on Valoria's price. Illustrative 35-day quantity of 7,700 units is about EUR 101,640. Not drafted: only worthwhile if Valoria's confirmed increase exceeds about 10%. Would be held for the Head of Supply Chain. Ranked 2, conditional.
- Expedite on an open order with SUP-VALO. Rejected: 50 days of cover against a 21-day buffer, so there is no shortage to buy off, and pulling stock forward ahead of an unconfirmed tariff spends money on an unknown.
- Re-allocation of committed supply between customers or plants. Rejected: no supply shortfall; the five open orders (EUR 1,116,000) are touched in value, not at risk of being missed.
- Wait without action. Rejected: the email costs nothing and resolves the main unknowns.
Drafts held for the Head of Supply Chain: email to SUP-VALO.
What it keeps for the next event:
> For a verified cost event on a multi-source part with cover above buffer, ask the incumbent for the real landed-cost change first, and compare it with the qualified alternate's premium before drafting any order.

## The autonomy ladder after this session

| Action type | Rung | Ceiling | Sound cases since last move | Not sound | Serious | Step up |
|---|---|---|---|---|---|---|
| supplier_email | Propose | Act with check | 0 | 0 | 0 | 0 of 5 sound cases since the last move. |
| expedite | Propose | Act with check | 0 | 0 | 0 | 0 of 5 sound cases since the last move. |
| new_po_qualified | Propose | Act with check | 0 | 0 | 0 | 0 of 5 sound cases since the last move. |
| new_po_unqualified | Watch | Watch | 0 | 0 | 0 | At its ceiling (Watch): a company rule, not a threshold. |

## What was held for you, drafted and not sent

| Draft | Part | Supplier / to | Amount | Action type | Held for |
|---|---|---|---|---|---|
| email | — | SUP-VALO | — | supplier_email | Head of Supply Chain |

## What was refused or held

| Agent | Step | Stopped or held by | Reason | Times |
|---|---|---|---|---|
| sourcing-options | draft_supplier_email | Control Tower rule P-006,P-009 | held for a person: Email to an address outside the company needs a named human approver. | 1 |

## How this page was made

- disruption-monitor: claude-fable-5-2, effort medium; sourcing-options: claude-fable-5-2, effort medium.
- Agent turns: disruption-monitor 2 (handed in), sourcing-options 4 (handed in).
- Tokens: 18,612 in, 2,921 out. 30.61 seconds from the first step to this page.
- The Control Tower recorded 11 steps for this session; chain intact.
- Checked afterwards against the answer key, which no agent was shown: 1 of 1 assessments agree on whether the event was material and which products it hit.
- Hand-ins the harness did not accept and handed back for correction: 0.
- The monitor has no tool that moves money or supply. Every purchase order and every email is held for the Head of Supply Chain. A step up on the ladder is never taken by an agent.
