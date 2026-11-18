"""Reach of action: how far an agent's permissions go inside the company.

The legal tier (classifier.py) answers "what does the law call this use?". It does
not say what the agent could do if it went wrong. An agent that suspends accounts
is "minimal" in law and still matters to the company. This rating answers the
second question, from the agent's own permission list and nothing else.

Fixed rules, highest level first. A tool this file does not know is rated as an
action (level 3) until someone classifies it, so a new permission never looks
harmless by default. Like the legal tier, the rating is a proposal for a person.
"""
from fnmatch import fnmatch

LEVELS = {
    4: "Can stop production",
    3: "Acts on accounts, systems or money",
    2: "Writes or proposes inside the company",
    1: "Reads only",
}
# level -> tool patterns. Checked in this order; the first match rates the tool.
RULES = [
    (4, ["network.isolate", "plc.write", "scada.write"]),
    (1, ["*.read", "*.simulate"]),
    (2, ["*.write", "*.propose", "ticket.update"]),
]
UNKNOWN = 3


def level_of(tool: str) -> int:
    for level, patterns in RULES:
        if any(fnmatch(tool, pattern) for pattern in patterns):
            return level
    return UNKNOWN


def reach(card: dict) -> dict:
    """The highest level any permitted tool reaches, and whether the agent uses it without a person."""
    tools = card["permissions"]["tools"]
    level = max((level_of(tool) for tool in tools), default=1)
    return {"agent_id": card["id"], "level": level, "name": LEVELS[level],
            "because": [tool for tool in tools if level_of(tool) == level] if level > 1 else [],
            "on_its_own": card["autonomy"] == "act", "signed_off_by": None}
