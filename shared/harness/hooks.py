"""The one door between an agent's tools and the Control Tower.

Shaped like the tool-call request hook of the OWASP Agent Control Standard (ACS,
v0.1.0 of 1 September 2026, as read on 20 November 2026): before a tool runs, the
harness announces the call, and the control layer answers allow, deny or ask.

  announcement  {"agent_id", "tool", "input"}, and for a call made by a named
                person: "approved_by" and "source"
  answer        {"decision": "allow" | "deny" | "ask", "reason", "rule",
                 "audit_seq", "executed", "verdict"}

"ask" means the call is held for a named person. "verdict" is the gateway's own
answer, unchanged.

Status, stated exactly: the shape is working, in process, calling Gateway.execute.
The ACS wire format, its signature and the ACS conformance test are designed, not
built. Until they are, this is our own hook that follows the standard's shape.
"""

ANSWERS = {"allow": "allow", "deny": "deny", "require_approval": "ask"}


class Refused(RuntimeError):
    """The Control Tower did not allow a step. The workflow stops; it never works around it."""

    def __init__(self, agent_id: str, tool: str, verdict: dict):
        super().__init__(f"{agent_id} may not use {tool}: {verdict['reason']} (rule {verdict['rule']})")
        self.verdict = verdict
        self.answer = ANSWERS.get(verdict["decision"], "deny")


def tool_call_request(gateway, announcement: dict) -> dict:
    """Announce one tool call to the Control Tower and return its answer.
    An answer the harness does not know is treated as deny: closed by default."""
    extra = {k: announcement[k] for k in ("approved_by", "source") if announcement.get(k) is not None}
    verdict = gateway.execute(announcement["agent_id"], announcement["tool"],
                              announcement.get("input") or {}, **extra)
    return {"decision": ANSWERS.get(verdict["decision"], "deny"), "reason": verdict["reason"],
            "rule": verdict["rule"], "audit_seq": verdict.get("audit_seq"),
            "executed": verdict.get("executed", False), "verdict": verdict}


def act(gateway, agent_id: str, tool: str, call: dict) -> dict:
    """Every step of every agent goes through here, and so through the hook.
    Allowed: the gateway's verdict comes back. Denied or held: Refused is raised."""
    answer = tool_call_request(gateway, {"agent_id": agent_id, "tool": tool, "input": call})
    if answer["decision"] != "allow":
        raise Refused(agent_id, tool, answer["verdict"])
    return answer["verdict"]
