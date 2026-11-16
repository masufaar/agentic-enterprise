# Business case: Complaint-to-Root-Cause Quality Agent

**Company:** Halden Industrial (fictional). **All figures are illustrative assumptions, not measured results.** Replace them with your own numbers.

## The problem

Quality investigations take weeks and recalls are scoped too broadly.

## The proposal

A customer complaint with photos goes to a vision agent that classifies the defect. A traceability agent walks the batch genealogy back to machine, shift and supplier lot, and the system drafts the 8D report.

## Value levers

| Lever | Assumption | Illustrative value |
|---|---|---|
| Investigation time saved | 1,200 complaints x 16 h x EUR 80/h x 40% | EUR 614,400 |

Further benefits, not quantified here:

- Narrower recall scope
- Faster, better-founded customer responses

## Cost

- **Build effort:** 60 to 80 hours for a thin working slice (estimate for one person working with an AI coding assistant).
- **Running cost:** Multimodal mid-tier model for defect classification and report drafting.

## Controls

Every agent in this solution is registered in the [AI Governance Control Tower](../01-ai-governance-control-tower/README.md), acts within written rules and is logged. Actions with high impact wait for a named person.

## Decision asked of the board

Give quality one traceable data chain from complaint to supplier lot.
