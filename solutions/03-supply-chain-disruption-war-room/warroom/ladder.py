"""The autonomy ladder: which response action types an agent may take at which level.

Fixed code, a control. No agent decides its own autonomy and no model is involved.

  watch -> propose -> act with check -> act alone

One rung per action type (a supplier email, an expedite, a purchase order to a
qualified alternate, a re-allocation, a purchase order to an unqualified supplier).
Three things move a type:

  a case           every response of a type is recorded with its outcome: ok,
                   failed, or serious (an unqualified supplier for a critical part,
                   or a response built on an event that was not real).
  a step down      taken by this code, at once, without asking anyone: a serious
                   case drops the type to 'propose'; too many failed cases drop it
                   one rung. It is recorded with the cases behind it.
  a step up        never taken by this code. When the cases since the last move are
                   enough and clean enough, the type is ready; the Head of Supply
                   Chain approves it, one rung at a time, up to the type's ceiling.

A step down can be reversed by the same role, with a reason, and that is recorded.
Thresholds, starting rungs and ceilings are data (data/ladder.json); the role is in
the company briefing. The record is an append-only file; when a Control Tower audit
trail is handed in, every move is written there as well.
"""
import json
from datetime import datetime, timezone
from pathlib import Path

from . import STATE, load

OUTCOMES = ("ok", "failed", "serious")
BY_THE_LADDER = "the autonomy ladder (fixed code)"


class NotAccepted(Exception):
    """A move was asked for that the ladder does not accept. Nothing changed."""


class Ladder:
    def __init__(self, config: dict | None = None, briefing: dict | None = None,
                 path: Path | None = None, audit=None):
        self.config = config or load("ladder.json")
        self.order = [level["id"] for level in self.config["levels"]]
        self.names = {level["id"]: level["name"] for level in self.config["levels"]}
        self.rules = self.config["rules"]
        self.start = {k: v for k, v in self.config["start"].items() if not k.startswith("_")}
        self.decider = (briefing or load("briefing.json"))["who_decides"]["role"]
        self.path = Path(path) if path else STATE / "ladder.jsonl"
        self.audit = audit

    # -- the record ------------------------------------------------------------
    def events(self) -> list[dict]:
        if not self.path.exists():
            return []
        return [json.loads(line) for line in self.path.read_text(encoding="utf-8").splitlines() if line]

    def _append(self, event: dict) -> dict:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        record = {"seq": len(self.events()) + 1,
                  "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"), **event}
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record) + "\n")
        return record

    def moves(self, type: str | None = None) -> list[dict]:
        return [e for e in self.events() if e["kind"] == "move" and type in (None, e["type"])]

    # -- where a type stands -----------------------------------------------------
    def types(self) -> list[str]:
        return list(self.start)

    def _known(self, type: str) -> None:
        if type not in self.start:
            raise NotAccepted(f"'{type}' is not an action type on the ladder.")

    def level(self, type: str) -> str:
        self._known(type)
        moves = self.moves(type)
        return moves[-1]["to"] if moves else self.start[type]

    def ceiling(self, type: str) -> str:
        return self.config["ceiling"].get(type, self.order[-1])

    def permits(self, type: str, needed: str) -> bool:
        return self.order.index(self.level(type)) >= self.order.index(needed)

    def cases(self, type: str) -> list[dict]:
        events = [e for e in self.events() if e.get("type") == type]
        last = max((i for i, e in enumerate(events) if e["kind"] == "move"), default=-1)
        return [e for e in events[last + 1:] if e["kind"] == "case"]

    def standing(self, type: str) -> dict:
        level, ceiling, cases = self.level(type), self.ceiling(type), self.cases(type)
        window = cases[-self.rules["window"]:]
        failed = sum(c["outcome"] != "ok" for c in window)
        serious = sum(c["outcome"] == "serious" for c in window)
        share = failed / len(window) if window else 0.0
        up = self.rules["step_up"]
        if self.order.index(level) >= self.order.index(ceiling):
            ready, waits_for = False, f"At its ceiling ({self.names[ceiling]}): a company rule, not a threshold."
        elif len(cases) < up["checked_cases_at_least"]:
            ready, waits_for = False, f"{len(cases)} of {up['checked_cases_at_least']} sound cases since the last move."
        elif serious > up["serious_findings_at_most"]:
            ready, waits_for = False, f"{serious} serious case(s) among the last {len(window)}."
        elif share > up["failed_share_at_most"]:
            ready, waits_for = False, (f"{failed} of the last {len(window)} cases were not sound; "
                                       f"at most {up['failed_share_at_most']:.0%} may.")
        else:
            ready, waits_for = True, f"The approval of the {self.decider}."
        return {"type": type, "level": level, "ceiling": ceiling, "cases_since_last_move": len(cases),
                "in_window": len(window), "failed": failed, "serious": serious, "failed_share": round(share, 3),
                "ready_for_step_up": ready,
                "next": self.order[self.order.index(level) + 1] if ready else None, "waits_for": waits_for}

    def table(self) -> list[dict]:
        return [self.standing(type) for type in self.types()]

    # -- what moves a type -------------------------------------------------------
    def _move(self, type: str, to: str, direction: str, by: str, why: str,
              evidence: list[str], reverses: int | None = None) -> dict:
        move = self._append({"kind": "move", "type": type, "from": self.level(type), "to": to,
                             "direction": direction, "by": by, "why": why, "evidence": evidence,
                             **({"reverses": reverses} if reverses is not None else {})})
        if self.audit is not None:
            self.audit.append({"source": "autonomy-ladder", "mode": "execute", "agent_id": None,
                               "tool": f"ladder.step_{direction}",
                               "params": {"type": type, "from": move["from"], "to": to, "evidence": evidence},
                               "decision": "executed", "rule": "LADDER", "reason": why,
                               "approved_by": None if by == BY_THE_LADDER else by})
        return move

    def record_case(self, type: str, ref: str, outcome: str, basis: str, finding: str = "") -> dict:
        """Record one response's outcome. Returns the case and, if it caused one, the step down."""
        self._known(type)
        if outcome not in OUTCOMES:
            raise NotAccepted(f"'{outcome}' is not an outcome. Use one of: {', '.join(OUTCOMES)}.")
        case = self._append({"kind": "case", "type": type, "ref": ref, "outcome": outcome,
                             "basis": basis, "finding": finding})
        return {"case": case, "move": self._step_down_if_needed(type, case)}

    def _step_down_if_needed(self, type: str, case: dict) -> dict | None:
        level = self.order.index(self.level(type))
        floor = self.order.index(self.rules["serious_finding_drops_to"])
        if case["outcome"] == "serious" and level > floor:
            return self._move(type, self.order[floor], "down", BY_THE_LADDER,
                              f"Serious case on {case['ref']}: {case['finding'] or 'no text given'}", [case["ref"]])
        down = self.rules["step_down"]
        window = self.cases(type)[-self.rules["window"]:]
        failed = [c for c in window if c["outcome"] != "ok"]
        if (level > 0 and len(window) >= down["checked_cases_at_least"]
                and len(failed) / len(window) > down["failed_share_above"]):
            return self._move(type, self.order[level - 1], "down", BY_THE_LADDER,
                              f"{len(failed)} of the last {len(window)} cases were not sound; "
                              f"the limit is {down['failed_share_above']:.0%}.",
                              [c["ref"] for c in failed])
        return None

    def approve(self, type: str, by: str) -> dict:
        self._known(type)
        if by != self.decider:
            raise NotAccepted(f"{by} cannot approve a step up. Only the {self.decider} can.")
        standing = self.standing(type)
        if not standing["ready_for_step_up"]:
            raise NotAccepted(f"{type} is not ready for a step up. {standing['waits_for']}")
        return self._move(type, standing["next"], "up", by,
                          f"{standing['in_window'] - standing['failed']} of the last {standing['in_window']} "
                          "cases were sound, with no serious case.",
                          [c["ref"] for c in self.cases(type)[-self.rules["window"]:]])

    def restore(self, type: str, by: str, why: str) -> dict:
        self._known(type)
        if by != self.decider:
            raise NotAccepted(f"{by} cannot reverse a step down. Only the {self.decider} can.")
        moves = self.moves(type)
        if not moves or moves[-1]["direction"] != "down":
            raise NotAccepted(f"The last move of {type} was not a step down; there is nothing to reverse.")
        if not (why or "").strip():
            raise NotAccepted("Reversing a step down needs a reason, which is recorded.")
        return self._move(type, moves[-1]["from"], "restored", by, why, moves[-1]["evidence"],
                          reverses=moves[-1]["seq"])
