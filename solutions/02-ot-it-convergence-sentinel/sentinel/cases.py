"""Case memory: what earlier nights taught, kept for the next one.

After every night, fixed code writes one case: the devices and accounts involved,
the steps taken on the office side, what the planner recommended, what the
challenger said, what the named person chose and the note that person added.
At the next night, the planner and the challenger can ask for the earlier cases
that share a device or an account with tonight's incident.

Who writes what:
  - the facts of a case are written by fixed code, never by an agent;
  - the lesson is the note of the named person who decided;
  - an agent may propose a change to the company briefing. The proposal is
    recorded with the case and shown on the page; it is never applied. A person
    edits the briefing.

Writing and reading cases go through the Control Tower like every other step.
"""
from datetime import datetime, timezone

import harness.cases

WRITER = "ot-briefing"  # fixed code; the registry card says so


class CaseBook(harness.cases.CaseBook):
    """The shared case book, with the Sentinel's own question: which earlier nights matter tonight."""
    writer = WRITER

    def matching(self, incident: dict, before: str) -> list[dict]:
        """Earlier cases that share a device or an account with this incident, newest first."""
        names = set(incident["path"]) | set(incident["accounts"])
        found = []
        for case in self.all():
            if case["case"] >= before:
                continue
            shared = sorted(names & (set(case["devices"]) | set(case["accounts"])))
            if shared:
                found.append({**summary(case), "shared_with_tonight": shared})
        return sorted(found, key=lambda c: c["case"], reverse=True)


def summary(case: dict) -> dict:
    """What an agent is shown of an earlier case: facts, the choice and the person's note."""
    keys = ("case", "night", "title", "date", "lines_touched", "first_response", "recommended",
            "challenger", "decision", "note_by_decider", "proposed_briefing_change")
    return {k: case.get(k) for k in keys}


def record(case_id: str, result: dict) -> dict:
    """The case of one night, from the night's result. Fixed code only."""
    incident, plan, challenge = result["incident"], result["plan"], result["challenge"]
    best = next((o for o in result["options"] if o["points"] == result["recommended"]), None)
    return {
        "case": case_id, "status": "waiting for decision", "night": result["night"], "title": result["title"],
        "date": datetime.now(timezone.utc).date().isoformat(), "incident": incident["id"],
        "devices": incident["path"], "accounts": incident["accounts"], "lines_touched": incident["lines_touched"],
        "first_response": [f"{s['step']} on {s['target']}" for s in result["first_response"]["steps"]],
        "recommended": {"response": best["name"], "lost_output_eur": best["cost_eur"]} if best else None,
        "challenger": challenge["verdict"] if challenge else "no verdict",
        "blind_spots": [b["tool"] for b in result.get("blind_spots", [])],
        "changed_by_new_alarm": result.get("news") is not None,
        "cases_read": result.get("cases_read", []),
        "proposed_briefing_change": (plan or {}).get("proposed_briefing_change") or None,
        "decision": None, "note_by_decider": None,
    }
