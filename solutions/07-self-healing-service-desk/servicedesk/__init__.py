"""Self-Healing Service Desk: who checks the ticket an AI agent closed?

Service desk suites now ship an agent that closes tickets without a person. The
closed ticket is then graded by the system that closed it. This solution adds what
the company owns on top of the suite it already runs:

  the connector   fixed code. The one door between an agent and the service desk
                  suite. Every call goes through the Control Tower first, and every
                  call that changes a ticket through the autonomy ladder as well.
  the ladder      fixed code, a control. Which ticket types may be worked at which
                  level: watch, propose, act with check, act alone. Checked cases
                  move a type; a named person approves each step up; a step down is
                  immediate, recorded and reversible.
  the suite       a stand-in for Halden's service desk suite, under an invented
                  vendor name. No real suite is connected.

The two agents of this solution, a resolution agent and a verifier that never
closes a ticket, are designed and not built yet. Nothing in this package calls a
language model.

Standard library only. All data is synthetic and belongs to the fictional company
Halden Industrial.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE = ROOT / "state"      # runtime files: the ladder's record (not committed)
REPORTS = ROOT / "reports"
SOLUTIONS = ROOT.parent

# The shared building blocks live in solution 01 and in shared/, and are used as they are.
CONTROL_TOWER = SOLUTIONS / "01-ai-governance-control-tower"
SHARED = SOLUTIONS.parent / "shared"
for folder in (CONTROL_TOWER, SHARED):
    if str(folder) not in sys.path:
        sys.path.insert(0, str(folder))

from harness import Refused, act, tool_call_request  # noqa: E402,F401  every step goes through the hook

RESOLUTION = "sd-resolution"  # the registry identity of the resolution agent
VERIFIER = "sd-verifier"      # the registry identity of the verifier agent
SUITE_AGENT = "Quillfield Auto-Resolve"  # the suite's own agent; the vendor name is invented


def load(name: str) -> dict:
    return json.loads((DATA / name).read_text(encoding="utf-8"))
