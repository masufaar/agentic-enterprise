"""The Alternative Sourcing Options Agent: it proposes a response, a person signs it.

One agent, one job, one exposure note at a time. Given a material exposure the
monitor mapped, it reasons over the responses open to Halden: a qualified
alternative supplier, an expedite, a supplier email, or a re-allocation it can only
recommend in words. It drafts the money-moving options; it does not send them.

The sign-off is not an instruction it could be talked out of: its card has autonomy
'act with approval', so the Control Tower holds every purchase order and every
email for the Head of Supply Chain. The connector refuses outright a purchase order
to an unqualified supplier for a part, and the Control Tower denies any spend over
the card's limit. The controls live in fixed code:
  - every draft goes through the connector and the Control Tower under this agent's
    identity, and comes back held for a named person, recorded and reversible;
  - a response is accepted only after the exposure and the alternatives have been
    read in this run;
  - an unqualified supplier is never the recommended choice;
  - every text stays within the briefing's limits.
"""
from harness import Refused
from harness.loop import Tool, ToolProblem

from . import SOURCING

ROLE = (
    "You are the alternative sourcing agent at Halden Industrial. You are given one exposure the monitor has mapped: "
    "a verified event that touches the bill of materials. You propose how to respond, ranked, with the cost and the "
    "lead time of each option: a qualified alternative supplier, an expedite on an open order, a supplier email, or a "
    "re-allocation of committed supply that you can only recommend in words. You draft the money-moving options; you "
    "do not send them. Every purchase order and every email you draft is held for the Head of Supply Chain to sign "
    "off, and you say so. You never bring in an unqualified supplier for a part, and the connector will refuse it. "
    "Read the exposure and the alternatives before you propose. Finish with propose_response. If it is not accepted, "
    "correct it and propose again.")


def system(briefing: dict) -> str:
    parts = [
        ROLE, "COMPANY BRIEFING", briefing["company"],
        "What matters, in this order:\n" + "\n".join(f"{n}. {t}" for n, t in enumerate(briefing["what_matters_in_this_order"], 1)),
        f"Risk appetite: {briefing['risk_appetite']}",
        f"Who signs off: the {briefing['who_decides']['role']}. {briefing['who_decides']['about']}",
        "Word limits: " + ", ".join(f"{k} {v} words" for k, v in briefing["word_limits"].items())]
    return "\n\n".join(parts)


def task(note: dict) -> str:
    return (f"Respond to the exposure from event {note['event']} (\"{note['headline']}\"): "
            f"kind {note['kind']}, parts {', '.join(note['affected_parts']) or 'none'}, "
            f"EUR {note['revenue_at_risk_eur']:,} at risk, {note['min_days_of_cover']} days of cover. "
            "Read it and the alternatives, then propose a ranked response.")


class Bench:
    """What the sourcing agent works from for one exposure."""

    def __init__(self, connector, briefing: dict, note: dict):
        self.connector, self.briefing, self.note = connector, briefing, note
        connector.exposure = note
        self.read_exposure = False
        self.read_alternates: set[str] = set()
        self.drafts: list[dict] = []   # held drafts created this run
        self.refused: list[dict] = []  # drafts the controls refused this run
        self.result = None

    def _call(self, operation: str, **given):
        try:
            out = self.connector.call(SOURCING, operation, **given)
        except Refused as refused:
            self.refused.append({"operation": operation, "rule": refused.verdict["rule"],
                                 "reason": refused.verdict["reason"]})
            raise ToolProblem(f"Refused by a control ({refused.verdict['rule']}): {refused.verdict['reason']}")
        if operation in ("draft_po", "draft_expedite", "draft_supplier_email"):
            self.drafts.append(out)
        return out

    def tools(self) -> list[Tool]:
        text = {"type": "string"}
        ident = {"type": "string"}
        amount = {"type": "integer"}

        def read_exposure(_):
            self.read_exposure = True
            return self._call("read_exposure")

        def read_part(given):
            return self._call("read_part", part=given["part"])

        def read_supplier(given):
            return self._call("read_supplier", supplier=given["supplier"])

        def list_alternates(given):
            self.read_alternates.add(given["part"])
            return self._call("list_alternates", part=given["part"])

        def draft_po(given):
            return self._call("draft_po", part=given["part"], supplier=given["supplier"], qty=given["qty"],
                              amount_eur=given["amount_eur"], reason=given["reason"])

        def draft_expedite(given):
            return self._call("draft_expedite", part=given["part"], supplier=given["supplier"], qty=given["qty"],
                              amount_eur=given["amount_eur"], reason=given["reason"])

        def draft_supplier_email(given):
            return self._call("draft_supplier_email", to=given["to"], subject=given["subject"], body=given["body"])

        return [
            Tool("read_exposure", "The monitor's exposure note for this event: the affected parts and products, the "
                 "revenue at risk and the days of cover.", read_exposure),
            Tool("read_part", "A part as the ERP shows it, with its days of cover.", read_part,
                 {"part": ident}, required=["part"]),
            Tool("read_supplier", "A supplier as the ERP shows it.", read_supplier,
                 {"supplier": ident}, required=["supplier"]),
            Tool("list_alternates", "The alternative suppliers qualified or not for a part, with lead time, a price "
                 "index and whether each is qualified.", list_alternates, {"part": ident}, required=["part"]),
            Tool("draft_expedite", "Draft an expedite (a rush order on an open purchase order). It is held for the "
                 "Head of Supply Chain.", draft_expedite,
                 {"part": ident, "supplier": ident, "qty": {"type": "integer"}, "amount_eur": amount, "reason": text},
                 required=["part", "supplier", "qty", "amount_eur", "reason"]),
            Tool("draft_po", "Draft a purchase order to an alternative supplier for a part. A qualified supplier is "
                 "held for the Head of Supply Chain; an unqualified one is refused.", draft_po,
                 {"part": ident, "supplier": ident, "qty": {"type": "integer"}, "amount_eur": amount, "reason": text},
                 required=["part", "supplier", "qty", "amount_eur", "reason"]),
            Tool("draft_supplier_email", "Draft an email to a supplier. It is held for the Head of Supply Chain.",
                 draft_supplier_email, {"to": text, "subject": text, "body": text},
                 required=["to", "subject", "body"]),
            Tool("propose_response", "Hand in the response. 'recommendation' is the ranked response in words, naming "
                 "which drafts are held for sign-off. 'options' lists each option considered. 'lesson' is one "
                 "sentence for the next event.", self.propose,
                 {"recommendation": text, "options": {"type": "array", "items": text}, "lesson": text},
                 required=["recommendation", "lesson"], hand_in=True)]

    def propose(self, given: dict) -> dict:
        problems = []
        recommendation = str(given.get("recommendation", "")).strip()
        lesson = str(given.get("lesson", "")).strip()
        options = [str(o).strip() for o in given.get("options") or []]
        if not self.read_exposure:
            problems.append("Read the exposure with read_exposure before you propose.")
        if self.note["material"] and self.note["affected_parts"] and not self.read_alternates:
            problems.append("Run list_alternates for an affected part before you propose a response.")
        if self.note["material"] and not self.drafts and "head of supply chain" not in recommendation.lower():
            problems.append("For a material exposure, either draft at least one held response, or recommend in words "
                            "that the Head of Supply Chain decide directly.")
        if not recommendation:
            problems.append("Say the ranked response in 'recommendation'.")
        if not lesson:
            problems.append("Say in 'lesson' what this case teaches for the next one.")
        from harness import checks
        problems += checks.too_long(self.briefing["word_limits"], recommendation=recommendation, lesson=lesson)
        if problems:
            raise ToolProblem("Not accepted. " + " ".join(problems))
        self.result = {"event": self.note["event"], "recommendation": recommendation, "options": options,
                       "lesson": lesson, "drafts_held": self.drafts, "refused": self.refused}
        return self.result
