"""One session, from a scenario file to the page for the Head of Supply Chain.

A scenario is a short list of steps on the synthetic supply chain:

  assess   the monitor maps one event onto the bill of materials and files an
           exposure note. Fixed code keeps it as a case for the next event.
  respond  the sourcing agent proposes a response to a material exposure. Its
           money-moving drafts are held for the Head of Supply Chain.
  decide   a decision of the Head of Supply Chain, given by the scenario file where
           a real run would wait for a person: record how a response turned out (a
           case on the ladder), approve a step up, or sign off a held draft.

Every session starts from the same morning: the systems as the data files show
them, the ladder on its starting rungs, an empty memory and its own audit trail.
After the last step, fixed code compares each exposure note with the answer key,
which no agent was shown, and writes the page.
"""
import json
import time
from pathlib import Path

from control_tower.audit import AuditLog
from control_tower.gateway import Gateway
from harness.loop import run_agent

from . import DATA, MONITOR, SOURCING, STATE, load
from . import monitor, sourcing
from . import page as page_module
from .connector import Connector
from .ladder import Ladder
from .systems import ERP, Feed

DEFAULT_SCENARIO = "single-source-halt"
AGENTS = {MONITOR: "disruption monitor", SOURCING: "sourcing agent"}


def load_scenario(name: str = DEFAULT_SCENARIO) -> dict:
    return json.loads((DATA / "scenarios" / f"{name}.json").read_text(encoding="utf-8"))


def scenarios() -> list[str]:
    return sorted(p.stem for p in (DATA / "scenarios").glob("*.json"))


class Session:
    def __init__(self, folder: Path, gateway: Gateway | None = None, briefing: dict | None = None,
                 ladder_config: dict | None = None):
        self.folder = Path(folder)
        self.folder.mkdir(parents=True, exist_ok=True)
        self.gateway = gateway or Gateway(audit=AuditLog(self.folder / "audit.jsonl"))
        self.briefing = briefing if briefing is not None else load("briefing.json")
        self.decider = self.briefing["who_decides"]["role"]
        self.erp, self.feed = ERP(), Feed()
        self.ladder = Ladder(config=ladder_config, briefing=self.briefing,
                             path=self.folder / "ladder.jsonl", audit=self.gateway.audit)
        self.connector = Connector(self.gateway, self.erp, self.feed, self.ladder, self.briefing)
        self.exposures: dict[str, dict] = {}
        self.cases: list[dict] = []
        self.runs: list[dict] = []
        self.log: list[dict] = []

    def assess(self, model, event_id: str) -> dict:
        self.connector.cases = self.cases
        bench = monitor.Bench(self.connector, self.briefing, event_id)
        run = run_agent(MONITOR, model, monitor.system(self.briefing), monitor.task(bench.event), bench.tools())
        self.runs.append(run)
        note = run["result"]
        if note is not None:
            self.exposures[event_id] = note
            self.cases.append({"about_id": bench.event["about"]["id"], "parts": note.get("affected_parts", []),
                               "event": event_id, "kind": note["kind"], "material": note["material"],
                               "lesson": note["lesson"]})
        entry = {"step": "assess", "event": event_id, "headline": bench.event["headline"],
                 "verified": bench.event["verified"], "ended": run["ended"], "note": note}
        self.log.append(entry)
        return entry

    def respond(self, model, event_id: str) -> dict:
        note = self.exposures.get(event_id)
        if note is None or not note["material"]:
            entry = {"step": "respond", "event": event_id, "skipped": "no material exposure to respond to"}
            self.log.append(entry)
            return entry
        bench = sourcing.Bench(self.connector, self.briefing, note)
        run = run_agent(SOURCING, model, sourcing.system(self.briefing), sourcing.task(note), bench.tools())
        self.runs.append(run)
        entry = {"step": "respond", "event": event_id, "ended": run["ended"], "result": run["result"],
                 "drafts_held": bench.drafts, "refused": bench.refused}
        self.log.append(entry)
        return entry

    def decide(self, decision: dict, note: str = "") -> dict:
        if "record_case" in decision:
            rc = decision["record_case"]
            done = self.ladder.record_case(rc["type"], rc["ref"], rc["outcome"], rc.get("basis", "the scenario file"),
                                           rc.get("finding", ""))
            article = "an" if rc["outcome"][0] in "aeiou" else "a"
            what = f"Recorded {article} {rc['outcome']} case for action type '{rc['type']}' ({rc['ref']})"
            if done["move"]:
                what += f"; the ladder stepped {done['move']['direction']} {rc['type']} to {self.ladder.names[done['move']['to']]}"
        elif "approve_step_up" in decision:
            done = self.ladder.approve(decision["approve_step_up"], self.decider)
            what = f"Approved the step up of {done['type']} from {self.ladder.names[done['from']]} to {self.ladder.names[done['to']]}"
        elif "sign_off" in decision:
            what = f"Signed off a held draft: {decision['sign_off']}"
        else:
            raise ValueError(f"A scenario cannot decide {decision}.")
        entry = {"step": "decide", "by": self.decider, "what": what, "given_by": "the scenario file", "note": note}
        self.log.append(entry)
        return entry


def score(exposures: dict[str, dict]) -> dict:
    """Compare each exposure note with the answer key. Fixed code, after the agents finished."""
    key = load("answer-key.json")["events"]
    compared = agreed = 0
    differences = []
    for event_id, note in exposures.items():
        truth = key.get(event_id)
        if truth is None:
            continue
        compared += 1
        said_products = set(note.get("affected_products", []))
        material_ok = note["material"] == truth["material"]
        products_ok = (not truth["material"]) or said_products == set(truth["hits_products"])
        if material_ok and products_ok:
            agreed += 1
        else:
            differences.append({"event": event_id, "said_material": note["material"], "truth_material": truth["material"],
                                "said_products": sorted(said_products), "truth_products": truth["hits_products"]})
    return {"events_compared": compared, "agreed": agreed, "differences": differences}


def run_scenario(model, name: str = DEFAULT_SCENARIO, folder: Path | None = None,
                 gateway: Gateway | None = None, briefing: dict | None = None) -> dict:
    chosen = load_scenario(name)
    started = time.monotonic()
    session = Session(folder or STATE / "sessions" / f"{name}-{int(time.time())}", gateway, briefing)
    for step in chosen["steps"]:
        if "assess" in step:
            session.assess(model, step["assess"])
        elif "respond" in step:
            session.respond(model, step["respond"])
        else:
            session.decide(step["decide"], step.get("note", ""))
    usage = {side: sum(run["tokens"][side] for run in session.runs) for side in ("input", "output")}
    audit = session.gateway.audit.records()
    held = [d for step in session.log if step["step"] == "respond" for d in step.get("drafts_held", [])]
    result = {
        "scenario": name, "title": chosen["title"], "question": chosen["question"], "decides": session.decider,
        "erp": session.erp.name, "feed": session.feed.name, "as_of": session.erp.as_of,
        "steps": session.log, "exposures": session.exposures, "ladder": session.ladder.table(),
        "ladder_names": session.ladder.names, "moves": session.ladder.moves(), "cases": session.cases,
        "held": held, "score": score(session.exposures),
        "refused": [{"agent": r["agent_id"], "rule": r["rule"], "reason": r["reason"],
                     "operation": (r.get("params") or {}).get("operation")}
                    for r in audit if r["decision"] in ("deny", "require_approval") and r.get("agent_id")],
        "handed_back": [{"agent": run["agent"], "tool": asked["tool"], "why": asked["result"]}
                        for run in session.runs for step in run["steps"] for asked in step["asked"]
                        if asked["failed"] and str(asked["result"]).startswith("Not accepted.")],
        "audit": {"records": len(audit), "chain": session.gateway.audit.verify()[1]},
        "models": {run["agent"]: run["model"] for run in session.runs},
        "runs": session.runs, "tokens": usage, "seconds_to_page": round(time.monotonic() - started, 2)}
    result["page"] = page_module.page(result)
    return result
