"""Tools the agents can call, and the facts the gateway reads from each call.

The agent hands the gateway the call exactly as it wants it carried out, and the
gateway, not the agent, carries it out. Before deciding, the gateway works out
the facts its rules depend on from the call itself (for an email: where it is
really going). Whatever the agent claims about those facts is overwritten.

The tools in version 0 are simulated: they record that they ran and do nothing
else. No email is sent and no system is touched.
"""
import re

ADDRESS = re.compile(r"[^@\s<>,;:\"']+@([a-z0-9-]+(?:\.[a-z0-9-]+)+)")
UNREADABLE = "unreadable-address"


def _email_facts(call: dict, company_domain: str) -> dict:
    """Where is this email really going? Looks at every recipient field."""
    recipients: list = []
    for field in ("to", "cc", "bcc"):
        value = call.get(field, [])
        recipients += value if isinstance(value, list) else [value]
    if not recipients:
        return {}  # no recipient at all: the rule then fails closed
    domains = []
    for recipient in recipients:
        match = ADDRESS.fullmatch(recipient.strip().lower()) if isinstance(recipient, str) else None
        domains.append(match.group(1) if match else UNREADABLE)
    outside = [d for d in domains if d != company_domain]
    return {"recipient_domain": outside[0] if outside else company_domain}


DERIVERS = {"email.send": _email_facts}


def derive_facts(tool: str, call: dict, company_domain: str) -> dict:
    deriver = DERIVERS.get(tool)
    return deriver(call, company_domain) if deriver else {}


class SimulatedTools:
    """Stands in for the real systems. Keeps a list of what was carried out."""

    def __init__(self):
        self.executed: list[dict] = []

    def run(self, agent_id: str, tool: str, call: dict) -> dict:
        self.executed.append({"agent_id": agent_id, "tool": tool, "call": call})
        result = {"executed": True, "simulated": True}
        if isinstance(call.get("rows"), int):
            result["rows_returned"] = call["rows"]  # a real tool returns at most this many
        return result
