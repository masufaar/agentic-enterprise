"""AI Governance Control Tower, version 0.

Standard library only. All data is synthetic (fictional company Halden Industrial).
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE = ROOT / "state"      # runtime files: audit trail, kill switch (not committed)
REPORTS = ROOT / "reports"  # published results (committed)
