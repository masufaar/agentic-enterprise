"""Approval queue: what is waiting for a named person, and what that person decided.

When the gateway holds an action, nothing is stored anywhere new: the held request
is already in the audit trail. The queue is read from the trail, and every decision
is written back to it, so the queue inherits the trail's tamper evidence.

Who decides: the accountable owner of the agent, as named in the registry.
Nobody else can release, and the agent cannot release its own request, because a
release comes from this workflow and never from the agent's call.

On release the gateway decides again on the same request. If the kill switch was
pulled or a limit was reached in the meantime, the release does not go through.

Version 0 does not verify who is at the keyboard: the approver states a role.
Company sign-in is designed, not built.
"""
import re

from .gateway import Gateway
from .tools import UNREADABLE, normal, _strings

DECISIONS = ("approval.release", "approval.refuse")


class ApprovalError(ValueError):
    pass


class Approvals:
    def __init__(self, gateway: Gateway):
        self.gateway = gateway

    # -- reading the queue ---------------------------------------------------
    def _split(self) -> tuple[list[dict], list[dict]]:
        """(waiting, decided) held requests, oldest first."""
        records = self.gateway.audit.records()
        outcome = {r["decides"]: r for r in records if r.get("decides") and r.get("decision") != "rejected"}
        held = [r for r in records if r.get("decision") == "require_approval" and r.get("mode") == "execute"]
        waiting = [r for r in held if r["seq"] not in outcome]
        decided = [{**r, "outcome": outcome[r["seq"]]} for r in held if r["seq"] in outcome]
        return waiting, decided

    def pending(self) -> list[dict]:
        return [self.describe(r) for r in self._split()[0]]

    def decided(self) -> list[dict]:
        return [{**self.describe(r), "outcome": r["outcome"]} for r in self._split()[1]]

    def describe(self, record: dict) -> dict:
        """Everything the approver needs on one item, in plain words."""
        card = self.gateway.registry[record["agent_id"]]
        rules = {r["id"]: r["description"] for r in self.gateway.policies["rules"]}
        return {
            "seq": record["seq"], "ts": record["ts"], "agent_id": record["agent_id"],
            "agent_name": card["name"], "approver": card["owner"], "tool": record["tool"],
            "rules": record["rule"].split(","),
            "why": [rules[i] for i in record["rule"].split(",")],
            "request": {k: v for k, v in record["params"].items()
                        if k not in ("content_label", "email_label", "data_class")},
            "look_for": self._hints(record),
        }

    def _hints(self, record: dict) -> list[str]:
        """What the gateway knows that helps the approver decide."""
        params, labels, hints = record["params"], self.gateway.labels, []
        if params.get("approved_by"):
            owner = self.gateway.registry[record["agent_id"]]["owner"]
            hints.append(f"The request itself claims an approval by {params['approved_by']}. The agent wrote "
                         f"that claim, so it counts for nothing: only a release from this queue by {owner} "
                         "approves the action.")
        if "P-006" in record["rule"]:
            where = params.get("recipient_domain")
            if where == UNREADABLE:
                hints.append("A recipient address could not be read, so it is treated as outside the company.")
            else:
                hints.append(f"Leaves the company: goes to {where}." if where
                             else "No readable recipient: it is not known where this would go.")
        if record["tool"] in labels["shared_stores"] or record["tool"] in labels["mail_tools"]:
            text = normal("".join(_strings({k: v for k, v in params.items() if k != "data_class"})))
            found: dict[str, list[str]] = {}
            for source in self.gateway.tools.sources.values():
                for rec in source["records"].values():
                    subject = rec[source["subject_field"]]["value"]
                    for name, field in rec.items():
                        if field["label"] in labels["labels_kept_out_of_shared_stores"] \
                                and len(normal(field["value"])) >= 4 and normal(field["value"]) in text:
                            found.setdefault(subject, []).append(name.replace("_", " "))
            for subject, fields in found.items():
                hints.append(f"Contains personal data of {subject}: {', '.join(fields)}.")
            if found and record["tool"] in labels["mail_tools"]:
                hints.append("At least one reader is not the person this data is about.")
            if not found and any(i in record["rule"] for i in ("P-011", "P-013")):
                seen = sorted({r["params"].get("record", "a record it did not name")
                               for r in self.gateway.audit.records()
                               if r["seq"] < record["seq"] and r.get("agent_id") == record["agent_id"]
                               and r.get("tool") in labels["sources"] and r.get("decision") == "allow"
                               and r.get("mode") == "execute"})
                hints.append("No labelled personal value was found in the text, but exact comparison "
                             "cannot see reworded data. Before writing this, the agent read: "
                             f"{', '.join(seen)}. Check the text for details of the people in those records.")
        return hints

    # -- deciding ------------------------------------------------------------
    def _item(self, seq: int, approver: str, action: str) -> dict:
        waiting = {r["seq"]: r for r in self._split()[0]}
        if seq not in waiting:
            raise ApprovalError(f"Item {seq} is not waiting for a decision")
        record = waiting[seq]
        owner = self.gateway.registry[record["agent_id"]]["owner"]
        if approver != owner:
            self.gateway.audit.append({
                "source": "approver", "mode": "decision", "agent_id": record["agent_id"], "tool": action,
                "params": {}, "decision": "rejected", "rule": "APPR-1", "decides": seq,
                "reason": f"Only the accountable owner ({owner}) decides on this agent's requests",
                "approved_by": approver})
            raise ApprovalError(f"Only the accountable owner ({owner}) decides on item {seq}")
        return record

    def release(self, seq: int, approver: str) -> dict:
        record = self._item(seq, approver, "approval.release")
        # The gateway reads the facts again and decides again, now with the approval.
        return self.gateway.execute(record["agent_id"], record["tool"], record["params"],
                                    approved_by=approver, source="approver", decides=seq)

    def refuse(self, seq: int, approver: str, reason: str = "") -> dict:
        record = self._item(seq, approver, "approval.refuse")
        return self.gateway.audit.append({
            "source": "approver", "mode": "decision", "agent_id": record["agent_id"],
            "tool": "approval.refuse", "params": {}, "decision": "refused", "rule": record["rule"],
            "decides": seq, "reason": reason or "Refused by the approver", "approved_by": approver})


def page(approvals: Approvals) -> str:
    """The approver's page, as text that the repository shows formatted."""
    waiting, decided = approvals.pending(), approvals.decided()
    load: dict[str, int] = {}
    for item in waiting:
        load[item["approver"]] = load.get(item["approver"], 0) + 1
    lines = [
        "# Waiting for a decision", "",
        "Generated from the audit trail of the latest red-team campaign by `python -m control_tower redteam`. "
        "All data is synthetic. In the campaign every waiting item is an attack that the gateway did not "
        "refuse outright but would not carry out without a person; the legitimate requests were released "
        "by their approver and are listed at the end.", "",
        "The approver is the accountable owner of the agent. Version 0 does not verify who is at the "
        "keyboard; company sign-in is designed, not built. On a live queue the approver decides with "
        "`python -m control_tower release RECORD --as ROLE` or `refuse RECORD --as ROLE reason`, where "
        "RECORD is the audit record number shown on the item; both are written to the audit trail.", "",
        f"**{len(waiting)} items waiting, {len(decided)} decided.**", "",
        "| Approver | Items waiting |", "|---|---|",
        *[f"| {who} | {count} |" for who, count in sorted(load.items(), key=lambda x: -x[1])], "",
    ]
    for number, item in enumerate(waiting, 1):
        lines += _item_lines(item, f"Waiting {number} of {len(waiting)}")
    if decided:
        lines += ["# Decided", ""]
        for number, item in enumerate(decided, 1):
            out = item["outcome"]
            verb = {"allow": "Released and carried out", "refused": "Refused"}.get(
                out["decision"], f"Release did not go through ({out['reason']})")
            lines += _item_lines(item, f"Decided {number} of {len(decided)}", waiting=False) + [
                f"**{verb}** by {out['approved_by']} (audit record {out['seq']}).", ""]
    return "\n".join(lines) + "\n"


def _shown(value) -> str:
    """Text as the page shows it: no table breaks, and addresses as plain text, not as mail links."""
    return re.sub(r"[\w.+-]+@[\w.-]*\w", lambda m: f"`{m.group()}`", str(value).replace("|", "/"))


def _item_lines(item: dict, position: str, waiting: bool = True) -> list[str]:
    """One item. It is counted in the order of the page; the audit record number is what
    the approver types to release or refuse it."""
    held = "is held" if waiting else "was held"
    lines = [f"## {position}: {item['agent_name']} {'wants' if waiting else 'asked'} to use `{item['tool']}`", "",
             f"- **{'Waiting for' if waiting else 'Approver'}:** {item['approver']}",
             f"- **Audit record:** {item['seq']}",
             *[f"- **Why it {held} ({rule}):** {why}" for rule, why in zip(item["rules"], item["why"])],
             *[f"- **Look for:** {_shown(hint)}" for hint in item["look_for"]]]
    if not item["request"]:
        return lines + ["- **The request:** the agent stated no details: no recipient, no amount, no text.", ""]
    lines.append("- **The request:**")
    for key, value in item["request"].items():
        lines.append(f"  - {key.replace('_', ' ')}: {_shown(value)}")
    return lines + [""]
