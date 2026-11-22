"""A stand-in for the service desk suite Halden already runs.

In a company this is the suite itself, reached through the vendor's own supported
connection (on 20 November 2026 the large suites offered an MCP server for this).
Here it is fixed code over synthetic files, under an invented vendor name:
Quillfield Service Desk, with its own agent Quillfield Auto-Resolve. No real suite
is connected.

The suite stays the system of record. It keeps two things apart, as a real one does:
what a ticket says (its note), and what was done in the system (its action log).

Nothing here decides who may do what. That is the connector's job (connector.py).
"""
from datetime import datetime, timedelta

from . import load  # noqa: F401  sets the path to the shared harness
from harness.loop import ToolProblem  # noqa: E402

CLOSED_STATES = ("closed",)


class SuiteProblem(ToolProblem):
    """The suite could not do what was asked. An agent is told why and can try something else."""


class Suite:
    name = "Quillfield Service Desk"

    def __init__(self, tickets: dict | None = None, activity: dict | None = None,
                 directory: dict | None = None, types: dict | None = None):
        source = tickets or load("tickets.json")
        self.as_of = source["as_of"]
        self.tickets = {t["id"]: dict(t) for t in source["tickets"]}
        self.activity = {k: {"actions": list(v["actions"]), "signals": list(v["signals"])}
                         for k, v in (activity or load("activity.json"))["tickets"].items()}
        self.directory = directory or load("directory.json")
        self.types = (types or load("ticket-types.json"))["types"]
        self.notes: dict[str, list[dict]] = {}   # what agents wrote on tickets through the connector

    # -- reading ---------------------------------------------------------------
    def ticket(self, ticket_id: str) -> dict:
        if ticket_id not in self.tickets:
            raise SuiteProblem(f"There is no ticket {ticket_id}.")
        return self.tickets[ticket_id]

    def get(self, ticket_id: str) -> dict:
        """A ticket as the suite shows it, with the notes written on it."""
        return {**self.ticket(ticket_id), "notes": [n for n in self.notes.get(ticket_id, []) if n["kind"] != "shadow"]}

    def search(self, state: str | None = None, type: str | None = None, closed_by: str | None = None,
               requester: str | None = None, about: str | None = None, group: str | None = None,
               limit: int = 25) -> list[dict]:
        """Tickets that match, oldest first: a short line each, not the whole ticket."""
        found = [t for t in self.tickets.values()
                 if (state is None or t["state"] == state) and (type is None or t["type"] == type)
                 and (closed_by is None or t.get("closed_by") == closed_by)
                 and (requester is None or t["requester"] == requester)
                 and (about is None or t["about"]["id"] == about)
                 and (group is None or t["suite_group"] == group)]
        found.sort(key=lambda t: t["opened"])
        return [{k: t.get(k) for k in ("id", "opened", "type", "state", "requester", "summary", "closed_by", "suite_group")}
                for t in found[:limit]]

    def owner(self, about: dict) -> dict:
        """Who owns what a ticket is about, from the company's own records."""
        kind, thing = about["kind"], about["id"]
        if kind == "account":
            who = [p for p, d in self.directory["people"].items() if d["account"] == thing]
        elif kind == "laptop":
            who = [p for p, d in self.directory["people"].items() if d["laptop"] == thing]
        elif kind == "resource":
            who = [self.directory["resources"][thing]["owner"]] if thing in self.directory["resources"] else []
        else:  # a printer or a plant-floor terminal belongs to a site, not to a person
            place = self.directory.get(f"{kind}s", {}).get(thing)
            return {"about": thing, "owner": None, "site": place["site"] if place else None}
        if not who:
            raise SuiteProblem(f"No owner is recorded for {thing}.")
        return {"about": thing, "owner": who[0], "site": self.directory["people"][who[0]]["site"]}

    def log(self, ticket_id: str) -> dict:
        """What was done in the system for this ticket, and what was seen afterwards."""
        self.ticket(ticket_id)
        return self.activity.get(ticket_id, {"actions": [], "signals": []})

    def later(self, ticket_id: str, days: int = 7) -> list[dict]:
        """Tickets the same requester, or anyone about the same thing, opened within 'days' of this one's closure."""
        ticket = self.ticket(ticket_id)
        if ticket["state"] not in CLOSED_STATES:
            raise SuiteProblem(f"{ticket_id} is not closed; there is nothing to follow up yet.")
        closed = datetime.fromisoformat(ticket["closed_at"])
        until = (closed + timedelta(days=days)).isoformat(timespec="minutes")
        return [{k: t[k] for k in ("id", "opened", "type", "requester", "about", "summary", "text", "state")}
                for t in sorted(self.tickets.values(), key=lambda t: t["opened"])
                if t["id"] != ticket_id and ticket["closed_at"] < t["opened"] <= until
                and (t["requester"] == ticket["requester"] or t["about"]["id"] == ticket["about"]["id"])]

    # -- changing --------------------------------------------------------------
    def _open(self, ticket_id: str) -> dict:
        ticket = self.ticket(ticket_id)
        if ticket["state"] != "open":
            raise SuiteProblem(f"{ticket_id} is {ticket['state']}; only an open ticket can be changed.")
        return ticket

    def note(self, ticket_id: str, actor: str, text: str, kind: str = "note") -> dict:
        """'shadow' notes are kept for comparison and are not shown on the ticket."""
        self._open(ticket_id)
        entry = {"at": self.as_of, "by": actor, "kind": kind, "text": text}
        self.notes.setdefault(ticket_id, []).append(entry)
        return entry

    def confirm(self, ticket_id: str, actor: str) -> dict:
        """Send a second-factor prompt to the registered phone of the account's owner.
        In this stand-in the owner confirms when the owner is the one who asked, and nobody confirms otherwise."""
        ticket = self._open(ticket_id)
        if ticket["about"]["kind"] != "account":
            raise SuiteProblem(f"{ticket_id} is not about an account; there is no owner's phone to ask.")
        confirmed = self.owner(ticket["about"])["owner"] == ticket["requester"]
        ticket["identity_check"] = "second factor" if confirmed else "second factor not confirmed"
        self.activity.setdefault(ticket_id, {"actions": [], "signals": []})["signals"].append(
            {"at": self.as_of, "kind": "second-factor prompt", "account": ticket["about"]["id"], "asked_by": actor,
             "result": "confirmed on the owner's registered phone" if confirmed else "not confirmed"})
        return {"ticket": ticket_id, "confirmed": confirmed, "identity_check": ticket["identity_check"]}

    def resolve(self, ticket_id: str, actor: str, action: str, note: str) -> dict:
        """Carry out one of the fixes the suite offers for this ticket type, and close the ticket."""
        ticket = self._open(ticket_id)
        offered = self.types[ticket["type"]]["actions"]
        if action not in offered:
            raise SuiteProblem(f"'{action}' is not a fix the suite offers for {ticket['type']}. "
                               f"Offered: {'; '.join(offered) or 'none'}.")
        ticket.update(state="closed", closed_at=self.as_of, closed_by=actor,
                      resolution={"action": action, "note": note})
        self.activity.setdefault(ticket_id, {"actions": [], "signals": []})["actions"].append(
            {"at": self.as_of, "actor": actor, "action": action, "target": ticket["about"]["id"]})
        return ticket

    def hand_over(self, ticket_id: str, actor: str, to: str, why: str) -> dict:
        ticket = self._open(ticket_id)
        ticket.update(state="handed over", handed_to=to, handed_over_by=actor)
        self.notes.setdefault(ticket_id, []).append(
            {"at": self.as_of, "by": actor, "kind": "hand-over", "text": f"Handed over to {to}: {why}"})
        return ticket
