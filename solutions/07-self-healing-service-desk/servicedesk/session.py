"""One session, from a scenario file to the page.

A scenario is a short list of steps on the synthetic service desk:

  verify   the verifier agent checks one closed ticket and files a finding
  work     the resolution agent works one open ticket
  decide   a decision of the role that decides, given by the scenario file where a
           real run would wait for a person. The page says so.

Every session starts from the same morning: the suite as the data files show it,
the ladder on its starting rungs, an empty case memory and its own audit trail. What
an agent learns in one step is there for the next step of the same session.

After the last step, fixed code compares the verifier's findings with the answer
key, which no agent was shown, and writes the page for the role that decides.
"""
import json
import time
from pathlib import Path

from control_tower.audit import AuditLog
from control_tower.gateway import Gateway
from harness.loop import run_agent

from . import DATA, RESOLUTION, STATE, VERIFIER, load
from . import page as page_module
from . import resolution, verifier
from .connector import Connector
from .findings import QUESTIONS, Findings
from .ladder import Ladder
from .memory import Memory
from .proposals import Proposals
from .suite import Suite

DEFAULT_SCENARIO = "sound-batch"
AGENTS = {RESOLUTION: "resolution agent", VERIFIER: "verifier agent"}


def load_scenario(name: str = DEFAULT_SCENARIO) -> dict:
    return json.loads((DATA / "scenarios" / f"{name}.json").read_text(encoding="utf-8"))


def scenarios() -> list[str]:
    return sorted(p.stem for p in (DATA / "scenarios").glob("*.json"))


class Session:
    """The working set of one session. Nothing in it outlives the folder it is given."""

    def __init__(self, folder: Path, gateway: Gateway | None = None, briefing: dict | None = None,
                 ladder_config: dict | None = None):
        self.folder = Path(folder)
        self.folder.mkdir(parents=True, exist_ok=True)
        self.gateway = gateway or Gateway(audit=AuditLog(self.folder / "audit.jsonl"))
        self.base_briefing = briefing if briefing is not None else load("briefing.json")
        self.decider = self.base_briefing["who_decides"]["role"]
        for agent in AGENTS:
            card = self.gateway.registry[agent]
            if card["owner"] != self.decider:
                raise ValueError(f"The briefing names the {self.decider} as the role that decides, but the "
                                 f"registry card of {agent} is owned by the {card['owner']}. They must be the same.")
        if self.gateway.registry[VERIFIER]["autonomy"] != "advise":
            raise ValueError(f"{VERIFIER} checks and reports; it runs only while its card says 'advise'.")
        self.ladder = Ladder(config=ladder_config, briefing=self.base_briefing,
                             path=self.folder / "ladder.jsonl", audit=self.gateway.audit)
        self.connector = Connector(self.gateway, Suite(), self.ladder, briefing=self.base_briefing)
        self.findings = Findings(self.gateway, self.ladder, self.folder / "findings.jsonl")
        self.memory = Memory(self.folder / "cases")
        self.proposals = Proposals(self.gateway, self.decider, self.folder / "proposals.json")
        self.runs: list[dict] = []
        self.log: list[dict] = []   # one entry per step, in order, for the page

    def briefing(self) -> dict:
        """The briefing in force: the file, plus the instruction of every approved proposal."""
        current = self.proposals.in_force(self.base_briefing)
        self.connector.briefing = current
        return current

    # -- the three kinds of step -------------------------------------------------
    def verify(self, model, ticket_id: str) -> dict:
        briefing = self.briefing()
        bench = verifier.Bench(self.connector, self.findings, self.memory, briefing, ticket_id)
        run = run_agent(VERIFIER, model, verifier.system(briefing), verifier.task(bench.ticket), bench.tools())
        self.runs.append(run)
        entry = {"step": "verify", "ticket": ticket_id, "type": bench.ticket["type"],
                 "closed_by": bench.ticket["closed_by"], "ended": run["ended"], "finding": run["result"],
                 "read": sorted(bench.read)}
        self.log.append(entry)
        return entry

    def work(self, model, ticket_id: str) -> dict:
        briefing = self.briefing()
        desk = resolution.Desk(self.connector, self.proposals, self.memory, briefing, ticket_id)
        rung = (self.ladder.names[self.ladder.level(desk.ticket["type"])]
                if desk.ticket["type"] in self.ladder.types() else "not on the ladder: hand over")
        run = run_agent(RESOLUTION, model, resolution.system(briefing), resolution.task(desk.ticket), desk.tools())
        self.runs.append(run)
        entry = {"step": "work", "ticket": ticket_id, "type": desk.ticket["type"], "summary": desk.ticket["summary"],
                 "rung": rung, "ended": run["ended"], "result": run["result"], "refused": desk.refused,
                 "instructions_in_force": [i["instruction"] for i in self.connector.instructions(desk.ticket)],
                 "cases_offered": len(self.memory.matching(desk.ticket))}
        self.log.append(entry)
        return entry

    def decide(self, decision: dict, note: str = "") -> dict:
        """A decision of the role that decides. In a scenario it is given by the file."""
        if "approve_proposal" in decision:
            done = self.proposals.approve(decision["approve_proposal"], self.decider)
            what = f"Approved proposal {done['number']} for a permanent fix: {done['incident'].rstrip('.')}"
        elif "approve_step_up" in decision:
            done = self.ladder.approve(decision["approve_step_up"], self.decider)
            what = f"Approved the step up of {done['type']} from {done['from']} to {done['to']}"
        else:
            raise ValueError(f"A scenario cannot decide {decision}.")
        entry = {"step": "decide", "by": self.decider, "what": what, "given_by": "the scenario file", "note": note}
        self.log.append(entry)
        return entry


def score(findings: list[dict]) -> dict:
    """Compare the findings with the answer key. Fixed code, after the agents have finished.
    An answer of 'cannot tell' is not counted for or against."""
    key = load("answer-key.json")["tickets"]
    answered = agreed = 0
    differences = []
    for finding in findings:
        truth = key.get(finding["ticket"])
        if truth is None:   # a ticket closed during the session has no line in the key
            continue
        for question in QUESTIONS:
            said = finding["answers"][question]
            if said == "cannot tell":
                continue
            answered += 1
            if (said == "yes") == truth[question]:
                agreed += 1
            else:
                differences.append({"ticket": finding["ticket"], "question": question, "said": said})
    return {"answers_compared": answered, "agreed": agreed, "differences": differences}


def run_scenario(model, name: str = DEFAULT_SCENARIO, folder: Path | None = None,
                 gateway: Gateway | None = None, briefing: dict | None = None) -> dict:
    """Run every step of a scenario and write the page."""
    chosen = load_scenario(name)
    started = time.monotonic()
    session = Session(folder or STATE / "sessions" / f"{name}-{int(time.time())}", gateway, briefing)
    for step in chosen["steps"]:
        if "verify" in step:
            session.verify(model, step["verify"])
        elif "work" in step:
            session.work(model, step["work"])
        else:
            session.decide(step["decide"], step.get("note", ""))
    usage = {side: sum(run["tokens"][side] for run in session.runs) for side in ("input", "output")}
    findings = session.findings.all()
    audit = session.gateway.audit.records()
    result = {
        "scenario": name, "title": chosen["title"], "question": chosen["question"], "decides": session.decider,
        "suite": session.connector.suite.name, "as_of": session.connector.suite.as_of,
        "steps": session.log, "findings": findings, "ladder": session.ladder.table(),
        "ladder_names": session.ladder.names, "moves": session.ladder.moves(),
        "proposals": session.proposals.all(), "cases": session.memory.all(),
        "score": score(findings),
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
