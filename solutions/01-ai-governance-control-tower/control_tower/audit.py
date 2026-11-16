"""Tamper-evident audit trail.

Each record carries the hash of the previous record. Changing or deleting any
earlier record breaks every hash after it, which verify() detects.
"""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from . import STATE

GENESIS = "0" * 64


def _digest(record: dict) -> str:
    body = json.dumps(record, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


class AuditLog:
    def __init__(self, path: Path | None = None):
        self.path = path or STATE / "audit.jsonl"
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def records(self) -> list[dict]:
        return self._records()

    def _records(self) -> list[dict]:
        if not self.path.exists():
            return []
        return [json.loads(line) for line in self.path.read_text().splitlines() if line]

    def append(self, event: dict) -> dict:
        records = self._records()
        record = {
            "seq": len(records) + 1,
            "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            **event,
            "prev_hash": records[-1]["hash"] if records else GENESIS,
        }
        record["hash"] = _digest(record)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, sort_keys=True) + "\n")
        return record

    def verify(self) -> tuple[bool, str]:
        prev = GENESIS
        for index, record in enumerate(self._records(), start=1):
            claimed = record.get("hash")
            body = {k: v for k, v in record.items() if k != "hash"}
            if record.get("seq") != index or body.get("prev_hash") != prev or _digest(body) != claimed:
                return False, f"chain broken at record {index}"
            prev = claimed
        return True, "chain intact"

    def __len__(self) -> int:
        return len(self._records())
