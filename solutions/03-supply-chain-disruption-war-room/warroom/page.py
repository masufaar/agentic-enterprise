"""The page for the Head of Supply Chain: what an event does to Halden, and what waits to be signed.

Fixed code puts the page together. The agents' words appear as theirs, in
quotation. Every figure on it is a trace of synthetic data or a count from the
session's own records: the ladder, the exposures, the held drafts and the Control
Tower's audit trail.
"""
from harness import page as frame

RULES = {"LADDER": "the autonomy ladder", "UNQUALIFIED": "no unqualified supplier for a part",
         "P-003": "Control Tower: over the spend limit", "P-005": "Control Tower: held for sign-off (spend)",
         "P-006": "Control Tower: held for sign-off (supplier email)", "P-009": "Control Tower: held for sign-off",
         "PERM-1": "Control Tower: not on the agent's permission list", "KILL": "Control Tower: kill switch"}


def _held(result: list[dict]) -> list[str]:
    if not result:
        return ["Nothing is held for your sign-off in this session."]
    lines = ["| Draft | Part | Supplier / to | Amount | Action type | Held for |", "|---|---|---|---|---|---|"]
    for d in result:
        target = d.get("supplier") or d.get("to", "")
        amount = f"EUR {d['amount_eur']:,}" if "amount_eur" in d else "—"
        lines.append(f"| {d['kind']} | {d.get('part', '—')} | {target} | {amount} | "
                     f"{d.get('action_type', '—')} | {d.get('held_for') or 'cleared'} |")
    return lines


def _decisions(result: dict) -> list[str]:
    lines = []
    for d in result["held"]:
        if d.get("held_for"):
            lines.append(f"- **Sign-off, for you:** {d['kind']} to {d.get('supplier') or d.get('to')}"
                         + (f", EUR {d['amount_eur']:,}" if 'amount_eur' in d else "") + ". Drafted, not sent.")
    for row in result["ladder"]:
        if row["ready_for_step_up"]:
            lines.append(f"- **Step up, for your approval:** {row['type']} from {result['ladder_names'][row['level']]} "
                         f"to {result['ladder_names'][row['next']]}. {row['in_window'] - row['failed']} of the last "
                         f"{row['in_window']} cases were sound.")
    for move in result["moves"]:
        if move["direction"] == "down":
            lines.append(f"- **Step down, already in force:** {move['type']} to {result['ladder_names'][move['to']]}, "
                         f"taken by {move['by']}. {move['why']} You can reverse it, with a reason that is recorded.")
    return lines or ["Nothing waits for your decision."]


def _exposures(result: dict) -> list[str]:
    if not result["exposures"]:
        return ["No event was assessed in this session."]
    lines = ["| Event | Material | Kind | Parts | Products | Revenue at risk | Cover (days) | Confidence |",
             "|---|---|---|---|---|---|---|---|"]
    for note in result["exposures"].values():
        rev = f"EUR {note['revenue_at_risk_eur']:,}" if note["material"] else "—"
        lines.append(f"| {note['event']} | {'yes' if note['material'] else 'no'} | {note['kind']} | "
                     f"{', '.join(note['affected_parts']) or '—'} | {', '.join(note['affected_products']) or '—'} | "
                     f"{rev} | {note['min_days_of_cover'] if note['material'] else '—'} | {note['confidence']} |")
    for note in result["exposures"].values():
        lines += ["", f"**{note['event']}** ({note['headline']}), the monitor's assessment:"]
        lines += frame.quote(note["assessment"])
        lines += ["What it keeps for the next event:"] + frame.quote(note["lesson"])
    return lines


def _responses(result: dict) -> list[str]:
    responses = [s for s in result["steps"] if s["step"] == "respond" and s.get("result")]
    if not responses:
        return ["No response was proposed in this session."]
    lines = []
    for step in responses:
        r = step["result"]
        lines.append(f"**Event {step['event']}**, the sourcing agent's recommendation:")
        lines += frame.quote(r["recommendation"])
        if r["options"]:
            lines += ["Options it weighed:"] + [f"- {o}" for o in r["options"]]
        if step["drafts_held"]:
            lines.append(f"Drafts held for the {result['decides']}: "
                         + "; ".join(f"{d['kind']} to {d.get('supplier') or d.get('to')}" for d in step["drafts_held"]) + ".")
        for ref in step["refused"]:
            lines.append(f"Refused on the way ({RULES.get(ref['rule'], ref['rule'])}): {ref['reason']}")
        lines += ["What it keeps for the next event:"] + frame.quote(r["lesson"]) + [""]
    return lines[:-1]


def _ladder(result: dict) -> list[str]:
    names = result["ladder_names"]
    lines = ["| Action type | Rung | Ceiling | Sound cases since last move | Not sound | Serious | Step up |",
             "|---|---|---|---|---|---|---|"]
    for row in result["ladder"]:
        lines.append(f"| {row['type']} | {names[row['level']]} | {names[row['ceiling']]} | "
                     f"{row['cases_since_last_move']} | {row['failed']} | {row['serious']} | "
                     f"{'Ready: ' if row['ready_for_step_up'] else ''}{row['waits_for']} |")
    return lines


def _refused(result: dict) -> list[str]:
    if not result["refused"]:
        return ["Nothing was refused or held in this session."]
    counted: dict[tuple, int] = {}
    for r in result["refused"]:
        key = (r["agent"], r["operation"] or "a call", r["rule"], r["reason"])
        counted[key] = counted.get(key, 0) + 1
    lines = ["| Agent | Step | Stopped or held by | Reason | Times |", "|---|---|---|---|---|"]
    for (agent, step, rule, reason), times in counted.items():
        held = "held for a person: " if rule and rule.startswith("P-0") and rule not in ("P-003",) else ""
        lines.append(f"| {agent} | {step} | {RULES.get(rule, f'Control Tower rule {rule}')} | {held}{reason} | {times} |")
    return lines


def page(result: dict) -> str:
    score = result["score"]
    decided = [s for s in result["steps"] if s["step"] == "decide"]
    scripted = any(m.startswith("scripted") for m in result["models"].values())
    lines = [
        "# Supply chain disruption: what does this event do to us, and who signs off?", "",
        f"For the {result['decides']}. Session: {result['title']}. Systems as of {result['as_of']}. All data is "
        f"synthetic (Halden Industrial). The risk feed ({result['feed']}) and the ERP ({result['erp']}) are stand-ins "
        "under invented vendor names; no real system is connected.", "",
        *(["**This page was produced with prepared replies in place of a model. It shows the fixed code around the "
           "agents working; it proves nothing about a model.**", ""] if scripted else []),
        f"**The question:** {result['question']}", "",
        "## What needs your decision", "", *_decisions(result), "",
        "## The exposure, mapped onto the bill of materials", "", *_exposures(result), "",
        "## What the sourcing agent proposed", "", *_responses(result), "",
        "## The autonomy ladder after this session", "", *_ladder(result), ""]
    if decided:
        lines += ["## Decisions taken in this session", ""]
        for step in decided:
            lines.append(f"- {step['what']}. Given by {step['given_by']}, standing in for the {step['by']}."
                         + (f" {step['note']}" if step["note"] else ""))
        lines.append("")
    lines += ["## What was held for you, drafted and not sent", "", *_held(result["held"]), "",
              "## What was refused or held", "", *_refused(result), "",
              "## How this page was made", "",
              "- " + "; ".join(f"{agent}: {model}" for agent, model in result["models"].items()) + ".",
              frame.agent_turns(result["runs"]) if result["runs"] else "- No agent ran.",
              f"- {frame.tokens(result['tokens'])} {result['seconds_to_page']} seconds from the first step to this page.",
              f"- The Control Tower recorded {result['audit']['records']} steps for this session; {result['audit']['chain']}.",
              f"- Checked afterwards against the answer key, which no agent was shown: {score['agreed']} of "
              f"{score['events_compared']} assessments agree on whether the event was material and which products it hit."
              + "".join(f" Differs: {d['event']} (said material={d['said_material']}, truth={d['truth_material']})."
                        for d in score["differences"]),
              f"- Hand-ins the harness did not accept and handed back for correction: {len(result['handed_back'])}.",
              "- The monitor has no tool that moves money or supply. Every purchase order and every email is held for "
              f"the {result['decides']}. A step up on the ladder is never taken by an agent.", ""]
    return "\n".join(lines)
