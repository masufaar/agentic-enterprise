"""OT/IT Convergence Sentinel, first slice.

A decision layer above the security tools a company already owns: it joins their
alerts into one incident, prices each possible response in lost output, asks for
the chosen response through the AI Governance Control Tower and writes one page
for the crisis team.

Two things live here. The first version (python -m sentinel run) is fixed rules
and no language model. The agents (python -m sentinel night) are language models
working in a loop inside the shared harness (shared/harness): see agents.py, night.py and decision.py. The rule-based
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
SHARED = ROOT.parent.parent / "shared"  # the shared agent harness, used by every solution
for folder in (CONTROL_TOWER, SHARED):
    if str(folder) not in sys.path:
        sys.path.insert(0, str(folder))


from harness import Refused, act, tool_call_request  # noqa: E402  every step goes through the hook


def load(name: str) -> dict:
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def when(text: str) -> datetime:
    return datetime.fromisoformat(text.replace("Z", "+00:00"))
