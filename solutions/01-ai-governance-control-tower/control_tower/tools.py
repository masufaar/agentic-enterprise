"""Tools the agents can call, and the facts the gateway reads from each call.

The agent hands the gateway the call exactly as it wants it carried out, and the
gateway, not the agent, carries it out. Before deciding, the gateway works out
the facts its rules depend on from the call itself (for an email: where it is
really going; for a write to a shared store: what the text really contains).
Whatever the agent claims about those facts is overwritten.

Data is labelled at its source: each field of a record carries a label
(data/tickets.json). The gateway compares text on its way to a shared store with
the labelled values at the source, so it does not depend on the agent's word.

The tools in version 0 are simulated: they record that they ran and do nothing
else. No email is sent and no system is touched.
"""
import json
import re

from . import DATA

ADDRESS = re.compile(r"[^@\s<>,;:\"']+@([a-z0-9-]+(?:\.[a-z0-9-]+)+)")
UNREADABLE = "unreadable-address"


def _email_facts(call: dict, context: dict) -> dict:
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
    company_domain = context["company_domain"]
    outside = [d for d in domains if d != company_domain]
    return {"recipient_domain": outside[0] if outside else company_domain}


def normal(text: str) -> str:
    """Lower case, all white space removed, so spacing and capitals cannot hide a value."""
    return "".join(text.split()).casefold()


def _strings(value):
    """Every piece of text anywhere in the call: title, body, tags, nested fields."""
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from _strings(item)
    elif isinstance(value, (list, tuple)):
        for item in value:
            yield from _strings(item)


def _shared_store_facts(call: dict, context: dict) -> dict:
    """What is really in this text? One of four answers, worst first:
      unreadable  no text to inspect: the rule refuses it
      personal    a value labelled personal at its source is in the text, or the agent says so
      unverified  no labelled value found, but this agent has handled labelled data,
                  so a reworded or encoded copy cannot be ruled out: a human decides
      clean       no labelled value found and the agent has handled none
    """
    content = call.get("content")
    if not isinstance(content, str) or not content.strip():
        return {"content_label": "unreadable"}
    text = normal("".join(_strings({k: v for k, v in call.items() if k != "data_class"})))
    if call.get("data_class") in context["kept_out"] or any(v in text for v in context["labelled_values"]):
        return {"content_label": "personal"}
    return {"content_label": "unverified" if context["handled_labelled_data"] else "clean"}


def derive_facts(tool: str, call: dict, context: dict) -> dict:
    if tool == "email.send":
        return _email_facts(call, context)
    if tool in context.get("shared_stores", {}):
        return _shared_store_facts(call, context)
    return {}


class SimulatedTools:
    """Stands in for the real systems. Keeps a list of what was carried out."""

    def __init__(self, sources: dict | None = None):
        self.executed: list[dict] = []
        # tool name -> the labelled records that tool hands out
        self.sources = {tool: json.loads((DATA / name).read_text(encoding="utf-8"))["records"]
                        for tool, name in (sources or {}).items()}

    def labelled_values(self, labels: list[str]) -> set[str]:
        """Every value carrying one of these labels at any source, ready for comparison.
        Values shorter than four characters are skipped: they would match by accident."""
        values = {normal(field["value"])
                  for records in self.sources.values() for record in records.values()
                  for field in record.values() if field["label"] in labels}
        return {v for v in values if len(v) >= 4}

    def run(self, agent_id: str, tool: str, call: dict) -> dict:
        self.executed.append({"agent_id": agent_id, "tool": tool, "call": call})
        result = {"executed": True, "simulated": True}
        if isinstance(call.get("rows"), int):
            result["rows_returned"] = call["rows"]  # a real tool returns at most this many
        record = self.sources.get(tool, {}).get(call.get("record"))
        if record is not None:
            result["record"] = record  # each field arrives with its label
        return result
