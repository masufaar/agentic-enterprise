"""Supply Chain Disruption War Room: who signs off when an AI agent reroutes supply?

A disruption-monitoring market already exists and is good at alerts. What is weak
is the next step: turning a published event into one owned decision, fast, and
never letting an agent move money or allocation on its own. This solution adds what
the company owns on top of the risk feed and the ERP it already runs:

  the connector   fixed code. The one door between an agent and Halden's systems.
                  Every call goes through the Control Tower first; every call that
                  would move money, allocation or a new supplier through the
                  autonomy ladder as well, and is held for a named person.
  the ladder      fixed code, a control. Which response action types an agent may
                  take at which level: watch, propose, act with check, act alone.
                  Sound cases move a type; a named person approves each step up; a
                  step down is immediate, recorded and reversible.
  the systems     stand-ins for the risk feed Halden subscribes to (Larkspur Supply
                  Signals) and its ERP/MRP (Fenmark MRP), under invented vendor
                  names. No real system is connected.

The two agents of this solution, a Supplier Disruption Monitor that only reads and
maps, and an Alternative Sourcing Options Agent whose money-moving drafts are held
for a named person, run on the shared harness. The monitor maps a published event
onto the bill of materials; it is a proposal, not an action. None of it is a
forecast: the agents act on events that have happened.

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

MONITOR = "disruption-monitor"   # the registry identity of the Supplier Disruption Monitor
SOURCING = "sourcing-options"    # the registry identity of the Alternative Sourcing Options Agent
ERP_NAME = "Fenmark MRP"                 # invented vendor name for Halden's ERP/MRP
FEED_NAME = "Larkspur Supply Signals"    # invented vendor name for the risk feed Halden subscribes to


def load(name: str) -> dict:
    return json.loads((DATA / name).read_text(encoding="utf-8"))
