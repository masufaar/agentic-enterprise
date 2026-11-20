import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
for folder in (ROOT, ROOT.parent / "01-ai-governance-control-tower", ROOT.parent.parent / "shared"):
    sys.path.insert(0, str(folder))
