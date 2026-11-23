"""The page for the role that decides which ticket types may be closed without a person.

Fixed code puts the page together. The agents' words appear as theirs, in
quotation. Every figure on it is counted from the session's own records: the
ladder, the findings, the proposals and the Control Tower's audit trail.
"""
from harness import page as frame

ASKED = {"fix_held": "Fix held", "requester_entitled": "Requester entitled", "record_matches": "Record matches"}
COUNTED = {"ok": "sound", "failed": "failed", "serious": "serious", "open": "not counted yet"}
RULES = {"LADDER": "the autonomy ladder", "HANDOVER": "hand-over rules", "PRIVACY": "a note names nobody else", "CLOSURE": "no closure without a fix", "IDENTITY": "who is asking",
         "BRIEFING": "the company briefing", "PERM-1": "Control Tower: not on the agent's permission list",
         "KILL": "Control Tower: kill switch"}


def _decisions(result: dict) -> list[str]:
    names, lines = result["ladder_names"], []
    for row in result["ladder"]:
        if row["ready_for_step_up"]:
            lines.append(f"- **Step up, for your approval:** {row['type']} from {names[row['level']]} to "
                         f"{names[row['next']]}. {row['in_window'] - row['failed']} of the last {row['in_window']} "
                         "checked cases were sound, with no serious finding.")
    for proposal in result["proposals"]:
        if proposal["status"] == "waiting for approval":
            lines.append(f"- **Permanent fix, for your approval:** proposal {proposal['number']}, "
                         f"{proposal['incident']} It is set out below.")
    for move in result["moves"]:
        if move["direction"] == "down":
            lines.append(f"- **Step down, already in force:** {move['type']} from {names[move['from']]} to "
                         f"{names[move['to']]}, taken by {move['by']}. {move['why']} "
                         "You can reverse it, with a reason that is recorded.")
    return lines or ["Nothing waits for your decision."]


def _proposals(result: dict) -> list[str]:
    if not result["proposals"]:
        return ["No permanent fix was proposed in this session."]
    lines = []
    for p in result["proposals"]:
        status = p["status"] + (f" by the {p['approved_by']}" if p["approved_by"] else "")
        lines += [f"**Proposal {p['number']}: {status}.** {p['incident']} Proposed while working {p['from_ticket']}; "
                  f"shown by {', '.join(p['tickets'])}.", *frame.quote(p["permanent_fix"]),
                  f"Standing instruction for {_scope(p)}:", *frame.quote(p["change"]["instruction"])]
        if p["change"].get("do_not_apply"):
            lines.append(("The connector now refuses" if p["status"] == "approved" else "Once approved, the connector refuses")
                         + " this fix for the incident: " + "; ".join(p["change"]["do_not_apply"]) + ".")
        lines.append("")
    return lines[:-1]


def _scope(proposal: dict) -> str:
    return ", ".join(f"{k.replace('_', ' ')} {v}" for k, v in proposal["change"]["applies_to"].items())


def _ladder(result: dict) -> list[str]:
    names = result["ladder_names"]
    lines = ["| Ticket type | Rung | Ceiling | Checked since last move | Failed | Serious | Step up |",
             "|---|---|---|---|---|---|---|"]
    for row in result["ladder"]:
        lines.append(f"| {row['type']} | {names[row['level']]} | {names[row['ceiling']]} | "
                     f"{row['checked_since_last_move']} | {row['failed']} | {row['serious']} | "
                     f"{'Ready: ' if row['ready_for_step_up'] else ''}{row['waits_for']} |")
    return lines


def _findings(result: dict) -> list[str]:
    if not result["findings"]:
        return ["No closed ticket was checked in this session."]
    lines = ["| Ticket | Type | Closed by | Fix held | Requester entitled | Record matches | Counted as |",
             "|---|---|---|---|---|---|---|"]
    for f in result["findings"]:
        a = f["answers"]
        lines.append(f"| {f['ticket']} | {f['type']} | {f['closed_by']} | {a['fix_held']} | "
                     f"{a['requester_entitled']} | {a['record_matches']} | {COUNTED[f['outcome']]} |")
    for f in result["findings"]:
        if f["outcome"] != "ok":
            lines += ["", f"**{f['ticket']}**, in the verifier's words"
                      + (f" (evidence: {', '.join(f['evidence'])})" if f["evidence"] else "") + ":"]
            lines += frame.quote(f["words"])
            if f["ladder_move"]:
                lines.append(f"On this finding the ladder moved {f['ladder_move']['type']} from "
                             f"{result['ladder_names'][f['ladder_move']['from']]} to "
                             f"{result['ladder_names'][f['ladder_move']['to']]}, at once.")
    again = [f["ticket"] for f in result["findings"] if f["outcome"] == "open"]
    if again:
        lines += ["", f"To be checked again when the evidence exists: {', '.join(again)}."]
    return lines


def _work(result: dict) -> list[str]:
    worked = [s for s in result["steps"] if s["step"] == "work"]
    if not worked:
        return ["No open ticket was worked in this session."]
    lines = []
    for step in worked:
        done = step["result"]
        lines.append(f"**{step['ticket']}**, {step['type']}: \"{step['summary']}\". Rung at the time: {step['rung']}.")
        if done is None:
            lines += [f"The agent did not hand in ({step['ended']}).", ""]
            continue
        did = done["did"] + (f": {done['action']}" if done.get("action") else "") \
            + (f", to the {done['handed_to']}" if done.get("handed_to") else "")
        lines.append(f"What the suite recorded: {did}.")
        lines += ["Why, in the agent's words:"] + frame.quote(done["reason"])
        for refusal in step["refused"]:
            lines.append(f"Refused on the way ({RULES.get(refusal['rule'], refusal['rule'])}), step "
                         f"'{refusal['step']}': {refusal['reason']}")
        if step["instructions_in_force"]:
            lines.append("Standing instruction in force for this ticket: " + " ".join(step["instructions_in_force"]))
        lines.append(f"Earlier cases the agent could read for this ticket: {step['cases_offered']}.")
        lines += ["What it keeps for the next ticket:"] + frame.quote(done["lesson"]) + [""]
    return lines[:-1]


def _refused(result: dict) -> list[str]:
    if not result["refused"]:
        return ["Nothing was refused in this session."]
    counted: dict[tuple, int] = {}
    for r in result["refused"]:
        key = (r["agent"], r["operation"] or "write to the knowledge base", r["rule"], r["reason"])
        counted[key] = counted.get(key, 0) + 1
    lines = ["| Agent | Step | Stopped by | Reason | Times |", "|---|---|---|---|---|"]
    for (agent, step, rule, reason), times in counted.items():
        held = "held for a person: " if rule and rule.startswith("P-") else ""
        lines.append(f"| {agent} | {step} | {RULES.get(rule, f'Control Tower rule {rule}')} | {held}{reason} | {times} |")
    return lines


def page(result: dict) -> str:
    score = result["score"]
    decided = [s for s in result["steps"] if s["step"] == "decide"]
    lines = [
        "# Service desk: which ticket types may be closed without a person?", "",
        f"For the {result['decides']}. Session: {result['title']}. Tickets as of {result['as_of']}. "
        f"All data is synthetic (Halden Industrial). The suite, {result['suite']}, is a stand-in under an invented "
        "vendor name; no real suite is connected.", "",
        *(["**This page was produced with prepared replies in place of a model. It shows the fixed code around the "
           "agents working; it proves nothing about a model.**", ""]
          if any(m.startswith("scripted") for m in result["models"].values()) else []),
        f"**The question:** {result['question']}", "",
        "## What needs your decision", "", *_decisions(result), "",
        "## The autonomy ladder after this session", "", *_ladder(result), "",
        "## What the verifier found", "", *_findings(result), "",
        "## What the resolution agent did", "", *_work(result), "",
        "## Permanent fixes proposed", "", *_proposals(result), ""]
    if decided:
        lines += ["## Decisions taken in this session", ""]
        for step in decided:
            lines.append(f"- {step['what']}. Given by {step['given_by']}, standing in for the {step['by']}."
                         + (f" {step['note']}" if step["note"] else ""))
        lines.append("")
    lines += ["## What was refused or held", "", *_refused(result), "",
              "## How this page was made", "",
              "- " + "; ".join(f"{agent}: {model}" for agent, model in result["models"].items()) + ".",
              frame.agent_turns(result["runs"]) if result["runs"] else "- No agent ran.",
              f"- {frame.tokens(result['tokens'])} {result['seconds_to_page']} seconds from the first step to this page.",
              f"- The Control Tower recorded {result['audit']['records']} steps for this session; {result['audit']['chain']}.",
              f"- Checked afterwards against the answer key, which no agent was shown: {score['agreed']} of "
              f"{score['answers_compared']} yes-or-no answers agree. An answer of 'cannot tell' is not counted."
              + ("".join(f" Differs: {d['ticket']}, {ASKED[d['question']].lower()}, the verifier said {d['said']}."
                         for d in score["differences"])),
              f"- Hand-ins the harness did not accept and handed back for correction: {len(result['handed_back'])}."
              + "".join(f" {h['agent']}, {h['tool']}: {h['why'].removeprefix('Not accepted. ')}" for h in result["handed_back"]),
              "- The verifier has no tool that closes or changes a ticket. A step up on the ladder is never taken "
              "by an agent.", ""]
    return "\n".join(lines)
