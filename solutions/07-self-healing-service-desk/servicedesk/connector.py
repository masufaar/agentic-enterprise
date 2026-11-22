"""The one connector: the only door between an agent and the service desk suite.

An agent never touches the suite. It asks the connector for one of a short list of
operations, shaped like the tools a suite's own connection offers to an outside
agent. For every call the connector does three things, in this order:

  1. A call that changes a ticket, from an agent whose registry card allows changes
     at all, must pass the autonomy ladder: is this ticket type on a rung that
     allows it? A ticket type that is handed over (plant floor, security) can only
     be handed over. A refusal is written to the Control Tower's audit trail.
  2. Every call, reading or changing, is announced to the Control Tower under the
     agent's own registry identity. The Control Tower decides and records it. An
     agent whose card has no tool that changes a ticket is refused there, on every
     ticket type and on every rung.
  3. Only then the suite carries it out.

Two company rules sit behind the ladder, for the two operations that apply a fix:

  who is asking   a fix on a ticket type that touches identity is carried out only
                  when the suite itself has confirmed the requester: the owner of
                  the account, by a signed-in session or a second factor; for an
                  access request, the approval of the owner of the folder or
                  application in the suite's log. What the ticket says does not count.
  the briefing    a fix that a standing instruction in the company briefing rules
                  out for an incident is not applied to it, and not proposed.

What the connector does not offer does not exist for an agent. It offers no way to
reopen or delete a ticket, and it does not serve the answer key.
"""
from harness import Refused, act

from . import load
from .ladder import Ladder
from .suite import Suite, SuiteProblem

READ, CHANGE = "ticket.read", "ticket.update"   # the names on the registry cards
STAFF = "service desk staff"

# operation -> (the Control Tower tool it counts as, the rung a ticket type must be on; None: no rung needed)
OPERATIONS = {
    "search_tickets": (READ, None),
    "get_ticket": (READ, None),
    "get_owner": (READ, None),
    "get_action_log": (READ, None),
    "get_later_tickets": (READ, None),
    "confirm_requester": (CHANGE, None),
    "add_note": (CHANGE, "watch"),
    "propose_fix": (CHANGE, "propose"),
    "resolve": (CHANGE, "act_with_check"),
    "hand_over": (CHANGE, None),
}


class Connector:
    def __init__(self, gateway, suite: Suite | None = None, ladder: Ladder | None = None,
                 briefing: dict | None = None):
        self.gateway = gateway
        self.suite = suite or Suite()
        self.ladder = ladder or Ladder(audit=gateway.audit)
        self.briefing = briefing if briefing is not None else load("briefing.json")

    def operations(self) -> list[str]:
        return list(OPERATIONS)

    def call(self, agent_id: str, operation: str, **given):
        if operation not in OPERATIONS:
            raise SuiteProblem(f"The connector offers no operation '{operation}'. "
                               f"It offers: {', '.join(OPERATIONS)}.")
        tool, rung = OPERATIONS[operation]
        ticket = self.suite.ticket(given["ticket"]) if operation != "search_tickets" else None
        card = self.gateway.registry.get(agent_id)
        if tool == CHANGE and card is not None and CHANGE in card["permissions"]["tools"]:
            self._ladder_gate(agent_id, operation, rung, ticket)
            if operation in ("resolve", "propose_fix"):
                self._fix_gate(agent_id, operation, ticket, given.get("action"))
        # An agent whose card allows no change at all is not sent to the ladder: the Control Tower refuses it.
        act(self.gateway, agent_id, tool, {"operation": operation, **given})
        return getattr(self, f"_{operation}")(agent_id, ticket, **{k: v for k, v in given.items() if k != "ticket"})

    # -- step 1: the ladder ------------------------------------------------------
    def _refuse(self, agent_id: str, operation: str, ticket: dict, rule: str, reason: str):
        record = self.gateway.audit.append({
            "source": "autonomy-ladder", "mode": "execute", "agent_id": agent_id, "tool": CHANGE,
            "params": {"operation": operation, "ticket": ticket["id"], "type": ticket["type"]},
            "decision": "deny", "rule": rule, "reason": reason, "approved_by": None})
        raise Refused(agent_id, operation, {"decision": "deny", "rule": rule, "reason": reason,
                                            "audit_seq": record["seq"]})

    def _ladder_gate(self, agent_id: str, operation: str, rung: str | None, ticket: dict) -> None:
        kind = self.suite.types[ticket["type"]]
        if kind["route"] == "hand over":
            if operation != "hand_over":
                self._refuse(agent_id, operation, ticket, "HANDOVER",
                             f"A {kind['name'].lower()} ticket is not worked here. "
                             f"It can only be handed over to the {kind['hand_over_to']}.")
            return
        if rung is not None and not self.ladder.permits(ticket["type"], rung):
            level = self.ladder.level(ticket["type"])
            self._refuse(agent_id, operation, ticket, "LADDER",
                         f"Ticket type '{ticket['type']}' is on the rung '{self.ladder.names[level]}'. "
                         f"'{operation}' needs '{self.ladder.names[rung]}' or higher. "
                         f"A step up is approved by the {self.ladder.decider}, never by an agent.")

    # -- the two company rules behind the ladder ---------------------------------
    def instructions(self, ticket: dict) -> list[dict]:
        """The standing instructions of the briefing that apply to this ticket."""
        return [i for i in self.briefing.get("standing_instructions", [])
                if all(ticket.get(key) == value for key, value in i["applies_to"].items())]

    def _fix_gate(self, agent_id: str, operation: str, ticket: dict, action: str) -> None:
        for instruction in self.instructions(ticket):
            if action in instruction.get("do_not_apply", []):
                self._refuse(agent_id, operation, ticket, "BRIEFING",
                             f"The company briefing rules this fix out for this incident: {instruction['instruction']}")
        if operation != "resolve" or not self.suite.types[ticket["type"]]["touches_identity"]:
            return
        if ticket["about"]["kind"] == "account":
            confirmed = ticket.get("identity_check") in self.briefing["entitlement"]["confirmations_that_count"]
            if not confirmed or self.suite.owner(ticket["about"])["owner"] != ticket["requester"]:
                self._refuse(agent_id, operation, ticket, "IDENTITY",
                             "The suite has not confirmed that the requester is the owner of this account "
                             f"(confirmation on the ticket: {ticket.get('identity_check', 'none')}). "
                             "What the ticket says does not count. Ask for a confirmation, or hand the ticket over.")
        elif not any(a["action"] == "approved the access request"
                     and a["actor"] == self.suite.owner(ticket["about"])["owner"]
                     for a in self.suite.log(ticket["id"])["actions"]):
            self._refuse(agent_id, operation, ticket, "IDENTITY",
                         "The owner of this folder or application has not approved the request in the suite. "
                         "Access is granted only after that approval.")

    # -- step 3: the suite -------------------------------------------------------
    def _search_tickets(self, agent_id, ticket, **filters):
        return self.suite.search(**filters)

    def _get_ticket(self, agent_id, ticket):
        return self.suite.get(ticket["id"])

    def _get_owner(self, agent_id, ticket):
        return self.suite.owner(ticket["about"])

    def _get_action_log(self, agent_id, ticket):
        return self.suite.log(ticket["id"])

    def _get_later_tickets(self, agent_id, ticket, days: int = 7):
        return self.suite.later(ticket["id"], days)

    def _confirm_requester(self, agent_id, ticket):
        return self.suite.confirm(ticket["id"], agent_id)

    def _add_note(self, agent_id, ticket, text: str):
        """On the rung 'watch' the note is kept for comparison and not shown to the person working the ticket."""
        shadow = self.ladder.level(ticket["type"]) == "watch"
        return self.suite.note(ticket["id"], agent_id, text, kind="shadow" if shadow else "note")

    def _propose_fix(self, agent_id, ticket, action: str, note: str):
        offered = self.suite.types[ticket["type"]]["actions"]
        if action not in offered:
            raise SuiteProblem(f"'{action}' is not a fix the suite offers for {ticket['type']}. "
                               f"Offered: {'; '.join(offered)}.")
        return self.suite.note(ticket["id"], agent_id, f"Proposed fix: {action}. {note}", kind="proposal")

    def _resolve(self, agent_id, ticket, action: str, note: str):
        return self.suite.resolve(ticket["id"], agent_id, action, note)

    def _hand_over(self, agent_id, ticket, why: str, to: str | None = None):
        """A handed-over ticket type goes where the company says, whatever the agent names."""
        kind = self.suite.types[ticket["type"]]
        return self.suite.hand_over(ticket["id"], agent_id, kind.get("hand_over_to") or to or STAFF, why)
