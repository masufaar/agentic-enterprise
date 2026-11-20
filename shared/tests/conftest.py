import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
for folder in (ROOT, ROOT.parent / "solutions" / "01-ai-governance-control-tower"):
    sys.path.insert(0, str(folder))
