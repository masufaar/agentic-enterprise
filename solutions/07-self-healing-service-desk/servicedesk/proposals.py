"""Proposals for a permanent fix: the same incident is not solved twice.

When an incident keeps coming back, the resolution agent may propose a permanent
fix, and with it a standing instruction for the company briefing. A proposal is
not a change. It is written to the knowledge base through the Control Tower, which
holds it for a named person; it takes effect only when the role that decides
approves it. Then fixed code adds the instruction to the briefing in force, and
from the next ticket on the agents read it and the connector enforces it.

An agent cannot approve its own proposal: the approval is passed in by the calling
workflow, and the Control Tower accepts it only from the accountable owner.
"""
import json
from pathlib import Path

from harness import tool_call_request
from harness.loop import ToolProblem

from . import RESOLUTION, STATE
from .ladder import NotAccepted


class Proposals:
    def __init__(self, gateway, decider: str, path: Path | None = None):
        self.gateway, self.decider = gateway, decider
        self.path = Path(path) if path else STATE / "proposals.json"

    def all(self) -> list[dict]:
        return json.loads(self.path.read_text(encoding="utf-8")) if self.path.exists() else []

    def _save(self, proposals: list[dict]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(proposals, indent=1), encoding="utf-8")

    @staticmethod
    def _call(proposal: dict) -> dict:
        return {"title": f"Proposed permanent fix: {proposal['incident']}",
                "content": f"{proposal['permanent_fix']} Standing instruction: {proposal['change']['instruction']}",
                "tickets": proposal["tickets"]}

    def submit(self, proposal: dict) -> dict:
        """Record a proposal. The Control Tower reads the text and holds it, or refuses it."""
        waiting = next((p for p in self.all() if p["status"] == "waiting for approval"
                        and p["change"]["applies_to"] == proposal["change"]["applies_to"]), None)
        if waiting:
            raise ToolProblem(f"Proposal {waiting['number']} for this incident already waits for the {self.decider}. "
                              "One proposal per incident; do not send a second.")
        answer = tool_call_request(self.gateway, {"agent_id": RESOLUTION, "tool": "kb.write",
                                                  "input": self._call(proposal)})
        if answer["decision"] == "deny":
            raise ToolProblem(f"The proposal was refused by the Control Tower: {answer['reason']} "
                              f"(rule {answer['rule']}). Write it without personal data.")
        proposals = self.all()
        kept = {"number": len(proposals) + 1, "status": "waiting for approval", "held_by_rule": answer["rule"],
                "audit_seq": answer["audit_seq"], "approved_by": None, **proposal}
        self._save(proposals + [kept])
        return kept

    def approve(self, number: int, by: str) -> dict:
        proposals = self.all()
        found = next((p for p in proposals if p["number"] == number), None)
        if found is None:
            raise NotAccepted(f"There is no proposal {number}.")
        if found["status"] != "waiting for approval":
            raise NotAccepted(f"Proposal {number} is already {found['status']}.")
        if by != self.decider:
            raise NotAccepted(f"{by} cannot approve a proposal. Only the {self.decider} can.")
        verdict = self.gateway.execute(RESOLUTION, "kb.write", self._call(found), approved_by=by,
                                       source="approval", decides=found["audit_seq"])
        if verdict["decision"] != "allow":
            raise NotAccepted(f"The Control Tower did not accept the approval: {verdict['reason']}")
        found.update(status="approved", approved_by=by)
        self._save(proposals)
        return found

    def in_force(self, briefing: dict) -> dict:
        """The briefing with the standing instructions of every approved proposal added."""
        added = [{**p["change"], "from_proposal": p["number"], "approved_by": p["approved_by"]}
                 for p in self.all() if p["status"] == "approved"]
        return {**briefing, "standing_instructions": list(briefing.get("standing_instructions", [])) + added}
