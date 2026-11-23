"""Case memory: what each ticket taught, kept for the next one.

After an agent has worked or checked a ticket, fixed code writes one case: the
facts of the ticket, what was done or found, and the one sentence the agent
handed in as its lesson. Before the next ticket, either agent can ask for the
earlier cases that share something with it: the same device or account, the same
group of incidents, or the same ticket type at the same site.

Who writes what:
  - the facts of a case are written by fixed code, never by an agent;
  - the lesson is the agent's own sentence, kept as a quotation;
  - writing and reading go through the Control Tower under the agent's own identity.

A case can change how the next ticket is handled. It cannot change a rule: rules
change only through a proposal that the role which decides approves (proposals.py).
"""
import harness.cases
from harness import act

SHOWN = ("case", "kind", "by", "ticket", "type", "site", "about", "suite_group", "closed_by", "did", "action",
         "answers", "outcome", "words", "lesson")


class Memory(harness.cases.CaseBook):
    def matching(self, ticket: dict) -> list[dict]:
        """Earlier cases that share something with this ticket, newest first, and what they share."""
        found = []
        for case in self.all():
            if case["ticket"] == ticket["id"]:
                continue
            shared = [words for same, words in (
                (case["about"] == ticket["about"]["id"], f"the same {ticket['about']['kind']}"),
                (bool(ticket.get("suite_group")) and case["suite_group"] == ticket["suite_group"],
                 "the same group of incidents"),
                (case["type"] == ticket["type"] and case["site"] == ticket["site"],
                 "the same ticket type at the same site")) if same]
            if shared:
                found.append({**{k: case.get(k) for k in SHOWN}, "shares_with_this_ticket": shared})
        return sorted(found, key=lambda c: c["case"], reverse=True)[:8]

    def read(self, gateway, agent_id: str, ticket: dict) -> dict:
        act(gateway, agent_id, "kb.read", {"what": "earlier cases", "ticket": ticket["id"]})
        found = self.matching(ticket)
        return {"earlier_cases": found,
                "note": "Each lesson is one agent's sentence about one ticket. It is not a rule and not a confirmation "
                        "of anyone's identity."} if found else \
            {"earlier_cases": [], "note": "No earlier case shares a device, an account, a group or a site with this ticket."}

    def keep(self, gateway, agent_id: str, kind: str, ticket: dict, **facts) -> dict:
        """Write the case of one ticket. Fixed code, under the identity of the agent whose work it records."""
        self.writer = agent_id
        return self.write(gateway, {
            "case": self.next_id(), "status": "closed", "kind": kind, "by": agent_id, "ticket": ticket["id"],
            "type": ticket["type"], "site": ticket["site"], "about": ticket["about"]["id"],
            "suite_group": ticket.get("suite_group"), "closed_by": ticket.get("closed_by"), **facts})
