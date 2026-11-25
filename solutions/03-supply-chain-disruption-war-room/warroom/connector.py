"""The one connector: the only door between an agent and Halden's systems.

An agent never touches a system. It asks the connector for one of a short list of
operations, shaped like the tools a risk feed and an ERP offer to an outside agent.
For every call the connector does three things, in this order:

  1. A call that would move money (a purchase order, an expedite) or send a supplier
     email, from an agent whose card allows it, must pass the autonomy ladder: is
     this action type on a rung that lets an agent even propose it? Two company
     rules sit here: an unqualified supplier for a part is never brought in by an
     agent (its action type is locked at 'watch'); and the spend stays under the
     card's limit, which the Control Tower enforces.
  2. Every call, reading or acting, is announced to the Control Tower under the
     agent's own registry identity. A money or email call by this agent (autonomy
     'act with approval') comes back 'held for a named person': it is drafted and
     waits for the Head of Supply Chain. It is never sent by the agent. A call over
     the spend limit is denied outright.
  3. Only then the system carries it out (here: records the draft, or returns data).

The monitor's card has no tool that changes anything, so the Control Tower refuses
it every acting call, on every action type. What the connector does not offer does
not exist for an agent: it offers no way to send a held draft, and it does not serve
the answer key.
"""
from harness import Refused, act, tool_call_request

from . import load
from .ladder import Ladder
from .systems import ERP, Feed, SystemProblem

# operation -> the Control Tower tool it counts as
TOOL = {
    "read_event": "news.read", "search_events": "news.read",
    "read_supplier": "supplier.read", "list_alternates": "supplier.read",
    "read_part": "erp.read", "trace_exposure": "erp.read", "read_exposure": "erp.read", "read_cases": "erp.read",
    "draft_supplier_email": "email.send", "draft_expedite": "erp.po.create", "draft_po": "erp.po.create",
}
# the money / email operations and the ladder action type each counts as
ACTION = {"draft_supplier_email": "supplier_email", "draft_expedite": "expedite"}  # draft_po resolved from the supplier
MONEY = {"draft_supplier_email", "draft_expedite", "draft_po"}
PROPOSE = "propose"   # the lowest rung at which an agent may put a response in front of a person


class Connector:
    def __init__(self, gateway, erp: ERP | None = None, feed: Feed | None = None,
                 ladder: Ladder | None = None, briefing: dict | None = None):
        self.gateway = gateway
        self.erp = erp or ERP()
        self.feed = feed or Feed()
        self.ladder = ladder or Ladder(audit=gateway.audit)
        self.briefing = briefing if briefing is not None else load("briefing.json")
        self.exposure: dict | None = None   # the monitor's exposure note, set by the session for the sourcing agent
        self.cases: list[dict] = []         # earlier cases, set by the session for the monitor to read

    def operations(self) -> list[str]:
        return list(TOOL)

    # -- action type for a purchase order ---------------------------------------
    def _po_action_type(self, part: str, supplier: str) -> str:
        primary = self.erp.parts.get(part, {}).get("primary_supplier")
        qualified = {a["supplier"] for a in self.erp.alternates(part) if a["qualified"]} | {primary}
        return "new_po_qualified" if supplier in qualified else "new_po_unqualified"

    def action_type(self, operation: str, given: dict) -> str:
        if operation == "draft_po":
            return self._po_action_type(given.get("part"), given.get("supplier"))
        return ACTION[operation]

    # -- the ladder gate ---------------------------------------------------------
    def _refuse(self, agent_id: str, operation: str, action_type: str, rule: str, reason: str):
        record = self.gateway.audit.append({
            "source": "autonomy-ladder", "mode": "execute", "agent_id": agent_id, "tool": TOOL[operation],
            "params": {"operation": operation, "action_type": action_type},
            "decision": "deny", "rule": rule, "reason": reason, "approved_by": None})
        raise Refused(agent_id, operation, {"decision": "deny", "rule": rule, "reason": reason,
                                            "audit_seq": record["seq"]})

    def _ladder_gate(self, agent_id: str, operation: str, action_type: str) -> None:
        if action_type == "new_po_unqualified":
            self._refuse(agent_id, operation, action_type, "UNQUALIFIED",
                         "The chosen supplier is not qualified for this part. An unqualified supplier for a part is "
                         f"never brought in by an agent; the {self.ladder.decider} decides that directly.")
        if not self.ladder.permits(action_type, PROPOSE):
            level = self.ladder.level(action_type)
            self._refuse(agent_id, operation, action_type, "LADDER",
                         f"Action type '{action_type}' is on the rung '{self.ladder.names[level]}'. An agent may put "
                         f"it to the {self.ladder.decider} only from '{self.ladder.names[PROPOSE]}' up. A step up is "
                         f"approved by the {self.ladder.decider}, never by an agent.")

    # -- the one entry point -----------------------------------------------------
    def call(self, agent_id: str, operation: str, **given):
        if operation not in TOOL:
            raise SystemProblem(f"The connector offers no operation '{operation}'. It offers: {', '.join(TOOL)}.")
        tool = TOOL[operation]
        card = self.gateway.registry.get(agent_id)
        if operation in MONEY and card is not None and tool in card["permissions"]["tools"]:
            action_type = self.action_type(operation, given)
            self._ladder_gate(agent_id, operation, action_type)
            return self._act(agent_id, operation, action_type, given)
        # a read, or an acting call by an agent whose card does not allow it (the Control Tower refuses that)
        act(self.gateway, agent_id, tool, {"operation": operation, **given})
        return getattr(self, f"_{operation}")(agent_id, **given)

    def _act(self, agent_id: str, operation: str, action_type: str, given: dict):
        """A money or email call: announce it, let the Control Tower hold it for a person, and record the draft."""
        announcement = {"agent_id": agent_id, "tool": TOOL[operation], "input": {"operation": operation, **given}}
        answer = tool_call_request(self.gateway, announcement)
        if answer["decision"] == "deny":
            raise Refused(agent_id, operation, answer["verdict"])
        draft = getattr(self, f"_{operation}")(agent_id, **given)
        held = answer["decision"] == "ask"
        draft["held_for"] = self.ladder.decider if held else None
        draft["status"] = (f"drafted, held for the {self.ladder.decider} to sign off" if held
                           else "drafted and cleared")
        draft["action_type"] = action_type
        draft["rule"] = answer["verdict"].get("rule")
        return draft

    # -- reads -------------------------------------------------------------------
    def _read_event(self, agent_id, event):
        return self.feed.event(event)

    def _search_events(self, agent_id, type=None, kind=None, about=None, verified=None, limit=25):
        return self.feed.search(type=type, kind=kind, about=about, verified=verified, limit=limit)

    def _read_supplier(self, agent_id, supplier):
        return self.erp.supplier(supplier)

    def _list_alternates(self, agent_id, part):
        return {"part": part, "alternates": self.erp.alternates(part)}

    def _read_part(self, agent_id, part):
        return self.erp.part(part)

    def _trace_exposure(self, agent_id, kind, id):
        return self.erp.trace({"kind": kind, "id": id})

    def _read_exposure(self, agent_id):
        if self.exposure is None:
            raise SystemProblem("No exposure note has been filed for this event yet.")
        return self.exposure

    def _read_cases(self, agent_id, about=None):
        """Earlier assessments that share a supplier, a part or a region with this event."""
        found = [c for c in self.cases if about is None or about in (c.get("about_id"), *c.get("parts", []))]
        return {"earlier_cases": found[-8:],
                "note": "Each lesson is the monitor's own sentence about one earlier event. It is not a rule."}

    # -- the acting calls (drafted, never sent) ----------------------------------
    def _draft_supplier_email(self, agent_id, to, subject, body):
        return self.erp.draft_email(agent_id, to, subject, body)

    def _draft_expedite(self, agent_id, part, supplier, qty, amount_eur, reason):
        return self.erp.draft_po(agent_id, part, supplier, qty, amount_eur, f"Expedite: {reason}")

    def _draft_po(self, agent_id, part, supplier, qty, amount_eur, reason):
        return self.erp.draft_po(agent_id, part, supplier, qty, amount_eur, reason)
