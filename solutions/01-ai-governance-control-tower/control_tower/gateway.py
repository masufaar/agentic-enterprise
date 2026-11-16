"""Policy gateway: every agent action passes through check() before it happens.

Decision order (first failure wins, and the gateway fails closed):
  1. Kill switch
  2. Agent must be in the registry        (no shadow agents)
  3. Agent must be approved by a named role
  4. Risk tier must not be "prohibited"
  5. Tool and data class must be on the agent's own permission list
  6. Daily volume limit per agent         (counted from the audit trail)
  7. Company rules in data/policies.json  (deny beats require-approval)
     For a write to a shared store, the rules act on a label the gateway works
     out itself by comparing the text with the labelled values at the source.
Every decision, allowed or not, is written to the audit trail.

The human approval is passed in by the calling workflow (approved_by). It is
never read from the agent's own request, so an agent cannot approve itself.

Two entry points:
  execute()  the agent hands over the call; the gateway reads the facts from
             the call itself, decides, and only then carries it out. This is
             the path agents use.
  check()    decides on stated values only, without carrying anything out.
             A dry run for people asking "would this be allowed?".
"""
import json
from datetime import datetime, timezone
from fnmatch import fnmatch
from pathlib import Path

from . import DATA, registry as registry_module
from .audit import AuditLog
from .classifier import classify
from .killswitch import KillSwitch
from .tools import SimulatedTools, derive_facts

OPS = {
    "gt": lambda a, b: a > b,
    "ne": lambda a, b: a != b,
    "eq": lambda a, b: a == b,
    "in": lambda a, b: a in b,
}


class Gateway:
    def __init__(self, registry: dict | None = None, policies_path: Path | None = None,
                 audit: AuditLog | None = None, killswitch: KillSwitch | None = None,
                 tools: SimulatedTools | None = None):
        self.registry = registry if registry is not None else registry_module.load()
        self.policies = json.loads((policies_path or DATA / "policies.json").read_text())
        self.audit = audit if audit is not None else AuditLog()
        self.killswitch = killswitch if killswitch is not None else KillSwitch()
        self.labels = self.policies["data_labels"]
        self.tools = tools if tools is not None else SimulatedTools(self.labels["sources"])

    # -- rule matching -------------------------------------------------------
    def _matches(self, rule: dict, card: dict, tier: str, tool: str, params: dict) -> bool:
        when = rule["when"]
        if "tools" in when and not any(fnmatch(tool, g) for g in when["tools"]):
            return False
        if "tools_except" in when and any(fnmatch(tool, g) for g in when["tools_except"]):
            return False
        if "tier" in when and tier not in when["tier"]:
            return False
        if "autonomy" in when and card["autonomy"] not in when["autonomy"]:
            return False
        if "param" in when:
            spec = when["param"]
            if spec["name"] not in params:
                return True  # fail closed: a missing value is treated as a violation
            if "value_from" in spec:
                source = spec["value_from"]
                limit = card["permissions"].get(source, self.policies.get(source))
            else:
                limit = spec["value"]
            try:
                return OPS[spec["op"]](params[spec["name"]], limit)
            except TypeError:
                return True  # fail closed on a value of the wrong type
        return True

    # -- volume limit --------------------------------------------------------
    def _rows_used_today(self, agent_id: str, tools: list[str]) -> int:
        """Rows this agent was already allowed to fetch today, read from the audit trail."""
        today = datetime.now(timezone.utc).date().isoformat()
        return sum(
            r["params"]["rows"] for r in self.audit.records()
            if r.get("agent_id") == agent_id and r.get("tool") in tools
            and r.get("decision") == "allow" and r.get("mode") == "execute"
            and r["ts"].startswith(today)
        )

    def _volume_violation(self, agent_id: str, tool: str, params: dict):
        limit = self.policies.get("volume_limit")
        if not limit or tool not in limit["tools"]:
            return None
        # "rows" is the cap the gateway passes to the tool, not a claim by the agent:
        # the tool returns at most that many rows. So it must be a positive whole number.
        rows = params.get("rows")
        if type(rows) is not int or rows <= 0:
            return "V-001", "A data request must state a positive number of rows, which the gateway enforces as the cap"
        cap = limit["rows_per_agent_per_day"]
        used = self._rows_used_today(agent_id, limit["tools"])
        if used + rows > cap:
            return "V-002", f"Daily volume limit reached ({used} of {cap} rows already used today)"
        return None

    # -- data labels ---------------------------------------------------------
    def _context(self, agent_id: str, tool: str) -> dict:
        """What the gateway itself knows and the agent cannot influence."""
        context = {"company_domain": self.policies["company_domain"],
                   "shared_stores": self.labels["shared_stores"]}
        if tool in self.labels["shared_stores"]:
            kept_out = self.labels["labels_kept_out_of_shared_stores"]
            context["kept_out"] = kept_out
            context["labelled_values"] = self.tools.labelled_values(kept_out)
            # Has this agent ever been handed records from a labelled source? Read from
            # the audit trail, like the volume count, so the agent cannot reset it.
            context["handled_labelled_data"] = any(
                r.get("agent_id") == agent_id and r.get("tool") in self.labels["sources"]
                and r.get("decision") == "allow" and r.get("mode") == "execute"
                for r in self.audit.records())
        return context

    # -- entry points --------------------------------------------------------
    def execute(self, agent_id: str, tool: str, call: dict | None = None,
                approved_by: str | None = None, source: str = "agent") -> dict:
        """Decide on the real call, then carry it out only if allowed."""
        call = call or {}
        facts = derive_facts(tool, call, self._context(agent_id, tool))
        logged = {**call, **facts}  # facts overwrite claims
        if facts.get("content_label") == "personal":
            # Refused text is kept out of the audit trail, or the trail would become
            # the next place the personal data is copied to.
            logged = {k: "[withheld: personal data]" if isinstance(v, (str, list, dict)) and k not in facts
                      and k != "data_class" else v for k, v in logged.items()}
        verdict = self.check(agent_id, tool, logged,
                             approved_by=approved_by, source=source, mode="execute")
        verdict["executed"] = False
        if verdict["decision"] == "allow":
            verdict["executed"] = self.tools.run(agent_id, tool, call)["executed"]
        return verdict

    def check(self, agent_id: str, tool: str, params: dict | None = None,
              approved_by: str | None = None, source: str = "agent",
              mode: str = "dry_run") -> dict:
        params = params or {}
        decision, rule, reason = self._decide(agent_id, tool, params, approved_by)
        record = self.audit.append({
            "source": source, "mode": mode, "agent_id": agent_id, "tool": tool, "params": params,
            "decision": decision, "rule": rule, "reason": reason, "approved_by": approved_by,
        })
        return {"decision": decision, "rule": rule, "reason": reason, "audit_seq": record["seq"]}

    def _decide(self, agent_id, tool, params, approved_by):
        if self.killswitch.is_killed(agent_id):
            return "deny", "KILL", "Kill switch is active for this agent"
        card = self.registry.get(agent_id)
        if card is None:
            return "deny", "REG-1", "Agent is not in the registry"
        if card["approval"].get("status") != "approved" or not card["approval"].get("approved_by"):
            return "deny", "REG-2", "Agent has not been approved by a named role"
        tier = classify(card)["tier"]
        if tier == "prohibited":
            return "deny", "REG-3", "Agent's use case is a prohibited practice"
        perms = card["permissions"]
        if tool not in perms["tools"]:
            return "deny", "PERM-1", f"Tool '{tool}' is not on this agent's permission list"
        data_class = params.get("data_class")
        if data_class is not None and data_class not in perms["data_classes"]:
            return "deny", "PERM-2", f"Data class '{data_class}' is not permitted for this agent"

        volume = self._volume_violation(agent_id, tool, params)
        if volume:
            return ("deny", *volume)

        hits = [r for r in self.policies["rules"] if self._matches(r, card, tier, tool, params)]
        for rule in hits:
            if rule["effect"] == "deny":
                return "deny", rule["id"], rule["description"]
        approvals = [r for r in hits if r["effect"] == "require_approval"]
        if approvals:
            ids = ",".join(r["id"] for r in approvals)
            if approved_by:
                return "allow", ids, f"Approved by {approved_by}"
            return "require_approval", ids, approvals[0]["description"]
        return "allow", None, "Within the agent's permissions and company rules"
