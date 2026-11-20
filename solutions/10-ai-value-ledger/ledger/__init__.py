"""AI Value Ledger: one line per agent, what it cost and what it returned.

The company spends on AI and cannot say what it gets back. This solution answers
that question for every agent in this repository, and says how good the answer is.

Two things live here:

  the ledger      fixed code. It reads the run records of the other solutions, prices
                  them from a dated price table, reads each benefit claim, and works
                  out the grade of the evidence behind it: measured, calculated or
                  claimed. Arithmetic belongs to code, not to a language model.
  the analyst     one agent, a language model working in a loop inside the shared
                  harness (shared/harness). It challenges each benefit claim as an
                  auditor would, names the proof that is missing, and writes the page
                  for the Chief AI Officer. It decides nothing and changes no budget.

Standard library only. All data is synthetic and belongs to the fictional company
Halden Industrial, except the cost of the Sentinel line, which is read from the real
run records in solutions/02-ot-it-convergence-sentinel/reports/runs.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
REPORTS = ROOT / "reports"
SOLUTIONS = ROOT.parent

# The shared building blocks live in solution 01 and in shared/, and are used as they are.
CONTROL_TOWER = SOLUTIONS / "01-ai-governance-control-tower"
SHARED = SOLUTIONS.parent / "shared"
for folder in (CONTROL_TOWER, SHARED):
    if str(folder) not in sys.path:
        sys.path.insert(0, str(folder))


from harness import Refused, act, tool_call_request  # noqa: E402,F401  every step goes through the hook

ANALYST = "value-ledger"  # the registry identity of the analyst agent


def load(name: str) -> dict:
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def eur(amount) -> str:
    """One way of writing money on a page and in an agent's text: EUR 120,000."""
    return f"EUR {round(amount):,}"


def usd(amount) -> str:
    return f"USD {amount:,.2f}"


def cents(amount) -> str:
    """A cost per run is often well under a euro, so it is written out in full."""
    return f"EUR {amount:,.2f}"
