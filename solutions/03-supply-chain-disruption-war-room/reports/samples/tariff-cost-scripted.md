# Supply chain disruption: what does this event do to us, and who signs off?

For the Head of Supply Chain. Session: A tariff on HSG-4 (a cost, not a stoppage). Systems as of 2026-02-13. All data is synthetic (Halden Industrial). The risk feed (Larkspur Supply Signals) and the ERP (Fenmark MRP) are stand-ins under invented vendor names; no real system is connected.

**This page was produced with prepared replies in place of a model. It shows the fixed code around the agents working; it proves nothing about a model.**

**The question:** A tariff raises the cost of a part used by four products. What is the exposure, and what is held for sign-off?

## What needs your decision

- **Sign-off, for you:** purchase_order to SUP-RHEIN, EUR 18,000. Drafted, not sent.

## The exposure, mapped onto the bill of materials

| Event | Material | Kind | Parts | Products | Revenue at risk | Cover (days) | Confidence |
|---|---|---|---|---|---|---|---|
| EV-02 | yes | cost | HSG-4 | PRD-A, PRD-C, PRD-D, PRD-F | EUR 1,116,000 | 50 | medium |

**EV-02** (25% tariff announced on imported aluminium housings), the monitor's assessment:
> A 25% tariff raises the landed cost of HSG-4, used by four products. It is a cost, not a stoppage: cover is 50 days and supply still flows.
What it keeps for the next event:
> A tariff is a cost exposure, not a stoppage; the response is price, not speed.

## What the sourcing agent proposed

**Event EV-02**, the sourcing agent's recommendation:
> Ranked: 1) a qualified PO to Rheinwerk for HSG-4 at a lower landed cost (held for sign-off); 2) an email to Valoria to re-open terms. No speed is needed; cover is 50 days.
Options it weighed:
- Qualified PO to Rheinwerk, EUR 18,000 (held)
- Re-open terms with Valoria (recommended)
Drafts held for the Head of Supply Chain: purchase_order to SUP-RHEIN.
What it keeps for the next event:
> For a cost exposure the clock is the tariff date, not the days of cover.

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
| purchase_order | HSG-4 | SUP-RHEIN | EUR 18,000 | new_po_qualified | Head of Supply Chain |

## What was refused or held

| Agent | Step | Stopped or held by | Reason | Times |
|---|---|---|---|---|
| sourcing-options | draft_po | Control Tower rule P-005,P-009 | held for a person: Purchase orders above EUR 10,000 need a named human approver (assumption). | 1 |

## How this page was made

- disruption-monitor: scripted stand-in (no model); sourcing-options: scripted stand-in (no model).
- Agent turns: disruption-monitor 3 (handed in), sourcing-options 4 (handed in).
- Tokens: 0 in, 0 out. 0.0 seconds from the first step to this page.
- The Control Tower recorded 5 steps for this session; chain intact.
- Checked afterwards against the answer key, which no agent was shown: 1 of 1 assessments agree on whether the event was material and which products it hit.
- Hand-ins the harness did not accept and handed back for correction: 0.
- The monitor has no tool that moves money or supply. Every purchase order and every email is held for the Head of Supply Chain. A step up on the ladder is never taken by an agent.
