"""OT/IT Convergence Sentinel, first slice.

A decision layer above the security tools a company already owns: it joins their
alerts into one incident, prices each possible response in lost output, asks for
the chosen response through the AI Governance Control Tower and writes one page
for the crisis team.

Two things live here. The first version (python -m sentinel run) is fixed rules
and no language model. The agents (python -m sentinel night) are language models
working in a loop: see loop.py, agents.py, night.py and decision.py. The rule-based
steps of the first version are the tools the agents call.

Standard library only. All data is synthetic (fictional company Halden Industrial)
and every tool is simulated.
"""
import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
REPORTS = ROOT / "reports"

# The shared building blocks live in solution 01 and are used as they are.
CONTROL_TOWER = ROOT.parent / "01-ai-governance-control-tower"
if str(CONTROL_TOWER) not in sys.path:
    sys.path.insert(0, str(CONTROL_TOWER))


class Refused(RuntimeError):
    """The Control Tower did not allow a step. The workflow stops; it never works around it."""

    def __init__(self, agent_id: str, tool: str, verdict: dict):
        super().__init__(f"{agent_id} may not use {tool}: {verdict['reason']} (rule {verdict['rule']})")
        self.verdict = verdict


def act(gateway, agent_id: str, tool: str, call: dict) -> dict:
    """Every step of every agent goes through here, and so through the gateway."""
    verdict = gateway.execute(agent_id, tool, call)
    if verdict["decision"] != "allow":
        raise Refused(agent_id, tool, verdict)
    return verdict


def load(name: str) -> dict:
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def when(text: str) -> datetime:
    return datetime.fromisoformat(text.replace("Z", "+00:00"))
