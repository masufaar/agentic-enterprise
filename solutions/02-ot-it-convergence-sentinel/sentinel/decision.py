"""The decision page, and the decision.

The page is put together by fixed code. Every euro figure on it is taken from the
pricing tool's own results; the agents' words are shown as theirs, in quotation.
The named person chooses one of the numbered responses. Only that choice, made in
the role the Control Tower registry names, carries anything out on the plant floor,
and it is written to the Control Tower's record.
"""
from control_tower.approvals import ApprovalError, Approvals

from .agents import CHALLENGER, FIRST, PLANNER
from .briefing import _clock, _stopped, eur
from .response import open_lines

STEP_WORDS = {"suspend_account": "Account suspended", "quarantine_workstation": "Device cut off the network",
              "close_remote_session": "Remote sessions closed"}


def _quote(text: str) -> list[str]:
    return [f"> {line}" for line in (text or "").splitlines() if line.strip()] or ["> (nothing written)"]


def page(result: dict) -> str:
    incident, plant, production = result["incident"], result["plant"], result["production"]
    plan, challenge, options, decides = result["plan"], result["challenge"], result["options"], result["decides"]
    names = {line["id"]: line["name"] for line in production["lines"]}
    best = next((o for o in options if o["points"] == result["recommended"]), None)
    nothing = next(o for o in options if not o["points"])
    safe = [o for o in options if not open_lines(o)]
    blind, news = result.get("blind_spots", []), result.get("news")
    models = sorted(set(result["models"].values()))
    lines = [
        f"# Decision page: incident {incident['id']} at {plant['plant']['name']}",
        "",
        f"Night: {result['title']}. Synthetic data, simulated tools. Agents run on: {', '.join(models)}. "
        "Every euro figure is calculated by the pricing tool from the assumptions listed at the end; none is a "
        "measured loss and none was written by an agent.",
        "",
        "## In short",
        "",
        f"An intruder moved from the office network to the plant floor between {_clock(incident['first_seen'])} and "
        f"{_clock(incident['last_seen'])} UTC and controls {len(incident['footholds'])} devices. "
        f"{len(nothing['lines_still_reachable'])} production lines are within reach.",
        "",
    ]
    for spot in blind:
        lines += [f"**Blind spot tonight: the {spot['tool']} on the {spot['watches']} sent nothing.** {spot['why']} "
                  f"Nobody can see whether the intruder is already on the {spot['watches']}. Lines there are marked "
                  "\"not watched\" below and are never counted as safe, so the prices of the narrow responses look "
                  "better than what is known.", ""]
    if news:
        before = news["plan_before"]["priced"]
        after = (f"now recommends {best['name']}, at {eur(best['cost_eur'])}" if best else "did not plan again")
        lines += [f"**The night changed after the first plan.** A new alarm arrived at "
                  f"{_clock(news['alerts'][-1]['time'])} UTC. Before it, the planner recommended {before['name']}, at "
                  f"{eur(before['cost_eur'])}; it {after}.", ""]
    if best is None:
        lines += ["**The planner agent did not hand in a plan.** The responses below were priced by the pricing tool "
                  f"alone, one step at a time. The {decides} decides without a recommendation.", ""]
    elif not safe:
        lines += [f"**No response available tonight closes every path.** The planner recommends: {best['name']}, "
                  f"at {eur(best['cost_eur'])} in lost output. It leaves "
                  f"{', '.join(names[l] for l in open_lines(best))} within the intruder's reach"
                  f"{' or unwatched' if best.get('lines_not_watched') else ''}, with "
                  f"{eur(best['still_at_stake_eur'])} at stake if it is encrypted.", ""]
    else:
        open_ = (" It leaves no line within reach." if not open_lines(best) else
                 f" **It leaves {', '.join(names[l] for l in open_lines(best))} within reach"
                 f"{' or unwatched' if best.get('lines_not_watched') else ''}.**")
        lines += [f"The planner recommends: {best['name']}, at {eur(best['cost_eur'])} in lost output.{open_}", ""]
    verdict = ("The challenger did not hand in a verdict." if not challenge else
               "The challenger agrees." if challenge["verdict"] == "agree" else
               "**The challenger objects.** Its argument is below, before the choice.")
    lines += [f"{verdict} Nothing has been disconnected on the plant floor: the choice is with the {decides}.", ""]

    late = {a["id"] for a in news["alerts"]} if news else set()
    lines += ["## What happened", "", "| Time (UTC) | Seen by | From | To | What |", "|---|---|---|---|---|"]
    lines += [f"| {_clock(s['time'])} | {s['side']} tool | {s['origin']} | {s['target']} | {s['text']}"
              f"{' (new alarm, after the first plan)' if s['id'] in late else ''} |" for s in incident["timeline"]]
    for spot in blind:
        lines.append(f"| - | {spot['watches']} | - | - | Nothing: the {spot['tool']} sent no alarm tonight. |")

    first = result["first_response"]
    lines += ["", "## Already done on the office side", "",
              "Taken by the first-response agent on its own. Each step can be undone and is in the Control Tower's record.", ""]
    if first["steps"]:
        lines += ["| Step | On | How it is undone | Record |", "|---|---|---|---|"]
        lines += [f"| {STEP_WORDS[s['step']]} | {s['target']} | {s['undo']} | {s['audit_record']} |" for s in first["steps"]]
    else:
        lines.append("No step was taken.")
    if first["left_alone"]:
        lines += ["", "What it left alone, in its own words:", "", *_quote(first["left_alone"])]

    lines += ["", "## The responses to choose from", "",
              "| No. | Response | Lost output | Lines stopped | Lines the intruder can still reach | Still at stake if those are encrypted |",
              "|---|---|---|---|---|---|"]
    for number, option in enumerate(options, 1):
        mark = " **(recommended)**" if option is best else ""
        reach = ", ".join([names[l] for l in option["lines_still_reachable"]]
                          + [f"{names[l]} (not watched)" for l in option.get("lines_not_watched", [])]) or "none"
        lines.append(f"| {number} | {option['name']}{mark} | {eur(option['cost_eur'])} | {_stopped(option)} | {reach} | "
                     f"{eur(option['still_at_stake_eur'])} |")
    for name, why in plant.get("unavailable_steps", {}).items():
        lines += ["", f"Not available tonight: {name}. {why}"]

    if news:
        before = news["plan_before"]
        lines += ["", "## The plan before the new alarm", "",
                  f"Recommended then: {before['priced']['name']}, at {eur(before['priced']['cost_eur'])} (priced before "
                  "the new alarm; out of date). The planner's reasoning then:", "", *_quote(before["why"])]
    if plan:
        lines += ["", "## The planner's reasoning", "", *_quote(plan["why"])]
        if plan["what_remains_open"]:
            lines += ["", "What remains open, in the planner's words:", "", *_quote(plan["what_remains_open"])]
    lines += ["", "## The counter-argument", ""]
    if not challenge:
        lines.append("None: the challenger agent did not hand in a verdict. The recommendation has not been challenged.")
    else:
        lines += [f"The challenger {'agrees' if challenge['verdict'] == 'agree' else 'objects'}:", "",
                  *_quote(challenge["argument"])]
        if challenge["alternative"] is not None:
            other = next(n for n, o in enumerate(options, 1) if "+".join(o["points"]) == challenge["alternative"])
            lines += ["", f"It proposes response {other} instead."]
        if challenge["what_nobody_knows"]:
            lines += ["", "What nobody knows, in the challenger's words:", "", *_quote(challenge["what_nobody_knows"])]
        if challenge["verdict"] == "object":
            first_plan = result["first_plan"]
            if plan["answer_to_challenger"]:
                kept = "kept its recommendation" if plan["recommended"] == first_plan["recommended"] \
                    else "changed its recommendation"
                lines += ["", f"The planner {kept} and answers:", "", *_quote(plan["answer_to_challenger"])]
            else:
                lines += ["", "The planner did not answer the objection. Its first plan stands unanswered."]

    if plan and plan.get("proposed_briefing_change"):
        lines += ["", "## A change to the company briefing, proposed by the planner", "",
                  *_quote(plan["proposed_briefing_change"]), "",
                  "Recorded with the case. Not applied: a person decides whether the briefing changes."]
    if result.get("case") and result["case"] != "no-case-memory":
        read = result.get("cases_read", [])
        lines += ["", "## Case memory", "",
                  f"This night is recorded as {result['case']}. "
                  + (f"Earlier cases read by the agents: {', '.join(read)}." if read else
                     "No earlier case was read: none shares a device or an account, or the agents did not ask.")]

    lines += ["", "## The decision", "",
              f"The {decides} chooses one response by its number: "
              f"`python -m sentinel decide NUMBER --as \"{decides}\" --note \"what the next night should know\"`. "
              "No other role can choose, and no agent can. The choice is written to the Control Tower's record."]
    waiting = [h for h in result["held"] if h["decision"] == "require_approval"]
    if waiting:
        lines += ["", "Filed with the Control Tower for the recommended response and held there:", "",
                  "| Step | Waiting for | Rules that hold it |", "|---|---|---|"]
        lines += [f"| {h['what']} | {decides} | {h['rule'].replace(',', ', ')} |" for h in waiting]

    rate = production["cost_per_stopped_line_hour_eur"]
    lines += ["", "## Assumptions behind the figures", "", f"- Cost of one stopped line-hour: {eur(rate)} (company profile)."]
    for a in production["assumptions"].values():
        value = "yes" if a["value"] is True else f"{a['value']} {a.get('unit', '')}".strip()
        lines.append(f"- {a['basis']} Value used: {value}.")
    lines += [f"- {p['name']}: held for {p['hold_hours']} hours. {p['hold_basis']}" for p in plant["isolation_points"]]
    lines += [
        "- Lost output is counted only for hours in which the schedule says the line would have run.",
        "- The office-side steps do not change the prices: a device the intruder already controls on the plant "
        "floor is assumed to stay under its control.",
        "",
        "## How this page was made", "",
        f"- Alarms read: {result['alerts']}; joined into this incident: {len(incident['alerts'])}; set aside: "
        f"{len(result['unrelated'])}. Joining is done by fixed rules, not by an agent.",
        f"- Responses priced tonight by the agents: {result['priced_tonight']}.",
        "- Agent turns: " + ", ".join(f"{r['agent']} {r['turns']} ({r['ended']})" for r in result["runs"]) + ".",
        *([f"- Time from the new alarm to this page: {news['seconds_from_new_alarm']} seconds."] if news else []),
        f"- Time from the last alarm handed over to this page: {result['seconds_to_page']} seconds. "
        f"Tokens: {result['tokens']['input']:,} in, {result['tokens']['output']:,} out.",
        "",
        "## What this page is not", "",
        "- Not a detection result: the alarms were written by hand for this night.",
        "- Not a forecast: the figures follow from the assumptions above and change with them.",
        "- Not proof that the agents are right. They can be wrong; that is why one challenges the other and a person decides.",
        "",
    ]
    return "\n".join(lines)


def decide(gateway, result: dict, number: int, role: str, note: str = "", cases=None) -> dict:
    """The named person chooses response 'number'. Returns what was carried out.
    The note is that person's lesson for the next night; it is written to the case memory."""
    owner = gateway.registry[PLANNER]["owner"]
    incident = f"{result.get('case', 'no-case-memory')}/{result['incident']['id']}"  # held steps are filed per case
    if not 1 <= number <= len(result["options"]):
        raise ApprovalError(f"There is no response {number} on the page")
    chosen = result["options"][number - 1]
    record = {"source": "approver", "mode": "decision", "agent_id": PLANNER, "tool": "decision.choose",
              "params": {"incident": incident, "response": number, "what": chosen["name"],
                         "lost_output_eur": chosen["cost_eur"], "recommended": chosen["points"] == result["recommended"],
                         "challenger": (result["challenge"] or {}).get("verdict", "no verdict")},
              "approved_by": role}
    if role != owner:
        gateway.audit.append({**record, "decision": "rejected", "rule": "APPR-1",
                              "reason": f"Only the {owner} decides on this incident"})
        raise ApprovalError(f"Only the {owner} decides on this incident")
    gateway.audit.append({**record, "decision": "chosen", "rule": None, "reason": f"Chosen by {role}"})
    approvals, carried = Approvals(gateway), []
    waiting = [i for i in approvals.pending()
               if i["agent_id"] == PLANNER and i["request"].get("incident") == incident]
    names = {p["id"]: p for p in result["plant"]["isolation_points"]}
    for item in waiting:  # requests filed for the recommendation: released if chosen, refused if not
        if item["request"]["isolation_point"] in chosen["points"]:
            carried.append({"what": item["request"]["what"], **approvals.release(item["seq"], role)})
        else:
            approvals.refuse(item["seq"], role, f"The {role} chose response {number} instead")
    filed = {i["request"]["isolation_point"] for i in waiting}
    for point in chosen["points"]:
        if point not in filed:
            verdict = gateway.execute(PLANNER, "network.isolate", {
                "isolation_point": point, "what": names[point]["name"], "plant": result["plant"]["plant"]["id"],
                "hold_hours": names[point]["hold_hours"], "incident": incident,
                "expected_cost_of_whole_response_eur": chosen["cost_eur"]}, approved_by=role, source="approver")
            carried.append({"what": names[point]["name"], **verdict})
    case = cases.get(result["case"]) if cases is not None and result.get("case") else None
    if case is not None:
        case.update({"status": "decided", "note_by_decider": note.strip() or None,
                     "decision": {"response": chosen["name"], "lost_output_eur": chosen["cost_eur"],
                                  "recommended": chosen["points"] == result["recommended"], "by": role}})
        cases.write(gateway, case)
    return {"chosen": chosen, "carried_out": carried}
