"""The verifier's findings: the company's own record of what was checked.

A finding answers three questions about one closed ticket: did the fix hold, was
the requester entitled, does the record match what was done. Each answer is yes,
no or cannot tell. The record is kept outside the service desk suite, because it
is the evidence the company owns about the suite and about every agent in it.

What a finding means for the autonomy ladder is decided here, in fixed code, and
not by the verifier:

  serious   the requester was not entitled, or the record does not match
  failed    the fix did not hold
  ok        three times yes
  open      at least one 'cannot tell' and no 'no': nothing is counted yet, and
            the ticket is listed to be checked again

Writing a finding goes through the Control Tower under the verifier's identity.
"""
import json
from pathlib import Path

from harness import act

from . import STATE, VERIFIER

QUESTIONS = ("fix_held", "requester_entitled", "record_matches")
ANSWERS = ("yes", "no", "cannot tell")


def outcome(answers: dict) -> str:
    if answers["requester_entitled"] == "no" or answers["record_matches"] == "no":
        return "serious"
    if answers["fix_held"] == "no":
        return "failed"
    return "ok" if all(answers[q] == "yes" for q in QUESTIONS) else "open"


class Findings:
    def __init__(self, gateway, ladder, path: Path | None = None):
        self.gateway, self.ladder = gateway, ladder
        self.path = Path(path) if path else STATE / "findings.jsonl"

    def all(self) -> list[dict]:
        if not self.path.exists():
            return []
        return [json.loads(line) for line in self.path.read_text(encoding="utf-8").splitlines() if line]

    def write(self, ticket: dict, answers: dict, evidence: list[str], words: str) -> dict:
        """Keep one finding, and hand its outcome to the ladder when the ticket type is on it."""
        result = outcome(answers)
        act(self.gateway, VERIFIER, "verification.write", {"ticket": ticket["id"], "outcome": result, **answers})
        finding = {"number": len(self.all()) + 1, "ticket": ticket["id"], "type": ticket["type"],
                   "closed_by": ticket["closed_by"], "answers": answers, "outcome": result,
                   "evidence": evidence, "words": words, "ladder_move": None}
        if result != "open" and ticket["type"] in self.ladder.types():
            move = self.ladder.record_case(ticket["type"], ticket["id"], result, "verified closure",
                                           closed_by=ticket["closed_by"], finding=words)["move"]
            finding["ladder_move"] = move and {k: move[k] for k in ("type", "from", "to", "direction", "why")}
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(finding) + "\n")
        return finding
