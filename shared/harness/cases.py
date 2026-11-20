"""Case memory: what earlier runs taught, kept for the next one.

One file per case. The facts of a case are written by fixed code, never by an
agent, and writing goes through the Control Tower like every other step. What a
case holds, and which earlier cases matter to a new one, is for each solution to say.
"""
import json
from pathlib import Path

from .hooks import act


class CaseBook:
    writer = "case-writer"  # the registry identity of the fixed code that writes; each solution sets its own

    def __init__(self, folder: Path):
        self.folder = Path(folder)

    def _files(self) -> list[Path]:
        return sorted(self.folder.glob("CASE-*.json")) if self.folder.exists() else []

    def all(self) -> list[dict]:
        return [json.loads(f.read_text(encoding="utf-8")) for f in self._files()]

    def next_id(self) -> str:
        return f"CASE-{len(self._files()) + 1:03d}"

    def get(self, case_id: str) -> dict | None:
        path = self.folder / f"{case_id}.json"
        return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None

    def write(self, gateway, case: dict) -> dict:
        act(gateway, self.writer, "cases.write", {"case": case["case"], "status": case["status"]})
        self.folder.mkdir(parents=True, exist_ok=True)
        (self.folder / f"{case['case']}.json").write_text(json.dumps(case, indent=1), encoding="utf-8")
        return case
