"""One night, from the last alarm to the decision page.

  1. The alarms of the tools the company owns are collected and joined (fixed code,
     the basic module of the first version).
  2. The first-response agent takes the office-side steps that can be undone.
  3. The planner prices responses and recommends one.
  If the night brings a new alarm after the first plan, the harness joins it to the
     incident, marks every price as out of date and sends the planner back to plan again.
  4. The challenger argues against it. If it objects, the planner answers: it keeps
     its recommendation and says why, or changes it.
  5. The harness files the plant-floor steps of the recommendation with the Control
     Tower, which holds them for the named person, and writes the decision page.

A night file can also declare a monitoring tool missing: its alarms are not read, and
the lines it would have watched are never priced as safe. At the end, the night is
written to the case memory (sentinel/cases.py), which the next night can read.

Nothing on the plant floor is carried out here. That happens only when the named
person chooses (sentinel/decision.py).
"""
import copy
import json
import time

from control_tower.audit import AuditLog
from control_tower.gateway import Gateway
from control_tower.killswitch import KillSwitch

from . import DATA, act, load
from . import agents, collection, correlation, decision, response
from . import cases as case_memory
from .agents import CHALLENGER, FIRST, PLANNER
from .loop import run_agent
from .response import open_lines

SIDES = {"office": {"side": "IT", "words": "office side"}, "plant": {"side": "OT", "words": "plant floor"}}

DEFAULT_NIGHT = "plant-04-0302"


def gateway(audit: AuditLog | None = None, killswitch: KillSwitch | None = None) -> Gateway:
    """The Control Tower gateway. All agents of this solution are cards in the Tower's registry."""
    return Gateway(audit=audit, killswitch=killswitch)


def load_night(name: str = DEFAULT_NIGHT) -> dict:
    """The data of one night. The default is the scripted night of the first version;
    any other night is that one plus what data/nights/<name>.json changes."""
    night = {"name": name, "title": "Plant 04, the scripted night: last alarm at 03:02",
             "plant": load("plant.json"), "production": load("production.json"),
             "office": load("events_office.json"), "floor": load("events_plant.json")}
    if name != DEFAULT_NIGHT:
        change = json.loads((DATA / "nights" / f"{name}.json").read_text(encoding="utf-8"))
        night["title"] = change.get("title", name)
        night["office"]["alerts"] += change.get("office_alerts_extra", [])
        night["floor"]["events"] += change.get("plant_events_extra", [])
        gone = change.get("unavailable_steps", {})
        night["plant"]["unavailable_steps"] = {
            p["name"]: gone[p["id"]] for p in night["plant"]["isolation_points"] if p["id"] in gone}
        night["plant"]["isolation_points"] = [p for p in night["plant"]["isolation_points"] if p["id"] not in gone]
        night["missing_feeds"] = change.get("missing_feeds", {})
        night["arrives_after_plan"] = change.get("arrives_after_plan", {})
    return night


def blind_spots(night: dict) -> list[dict]:
    tools = {"office": night["office"]["source_tool"], "plant": night["floor"]["sensor"]}
    return [{"feed": feed, "tool": tools[feed], "side": SIDES[feed]["side"], "watches": SIDES[feed]["words"],
             "why": why} for feed, why in night.get("missing_feeds", {}).items()]


def _task_planner(first: list) -> str:
    done = "; ".join(f"{s['step']} on {s['target']}" for s in first) or "none"
    return ("The alarms of tonight have been joined into one incident. Office-side steps already taken by the "
            f"first-response agent: {done}. Prepare the decision for the plant floor.")


def _task_challenger(plan: dict, desk) -> str:
    shown = {key: desk.priced[key]["name"] for key in plan["options"]}
    return ("The planner has handed in this plan. Step ids of each response it puts before the decider: "
            f"{json.dumps(shown)}. Recommended: {plan['recommended'] or 'do nothing'}. "
            f"Its reason: {plan['why']} What it says remains open: {plan['what_remains_open'] or 'nothing'} "
            "Challenge it.")


def _task_news(plan: dict, desk, alerts: list[dict]) -> str:
    seen = "; ".join(f"{a['time'][11:16]} UTC, {a['origin']} to {a['target']}: {a['text']}" for a in alerts)
    return (f"A new alarm arrived after you handed in your plan: {seen} The incident has been updated and every "
            f"price made before is out of date. Your plan recommended {desk.stale[plan['recommended']]['name']}. "
            "Read the incident again, price again and submit a new plan: keep your recommendation or change it, "
            "and say in 'why' what the new alarm changed.")


def _task_answer(challenge: dict) -> str:
    other = f" It proposes instead: {challenge['alternative']}." if challenge["alternative"] is not None else ""
    return (f"The challenger objects to your recommendation. Its argument: {challenge['argument']}{other} "
            f"What it says nobody knows: {challenge['what_nobody_knows'] or 'nothing'} "
            "Check its point with the tools. Then submit your plan again: keep your recommendation or change it, "
            "and answer the challenger in 'answer_to_challenger'.")


def run_night(models, gate: Gateway | None = None, night: str = DEFAULT_NIGHT, briefing: dict | None = None,
              cases: case_memory.CaseBook | None = None) -> dict:
    """'models' is one model for all three agents, or a model per agent identity.
    'cases' is the case memory; without it the night neither reads nor writes cases."""
    model_of = models if isinstance(models, dict) else {a: models for a in (FIRST, PLANNER, CHALLENGER)}
    gate = gate if gate is not None else gateway()
    briefing = briefing if briefing is not None else load("briefing.json")
    owner = gate.registry[PLANNER]["owner"]
    if briefing["who_decides"]["role"] != owner:
        raise ValueError(f"The briefing names the {briefing['who_decides']['role']} as the person who decides, the "
                         f"Control Tower registry names the {owner}. They must agree before a night is run.")
    data = load_night(night)
    started = time.monotonic()
    collected = collection.collect(gate, data)
    found = correlation.correlate(gate, collected)
    blind = blind_spots(data)
    case_id = cases.next_id() if cases is not None else "no-case-memory"
    result = {"night": data["name"], "title": data["title"], "decides": owner, "plant": collected["plant"],
              "production": data["production"], "alerts": len(collected["alerts"]), "case": case_id,
              "unrelated": found["unrelated"], "incident": None, "runs": [], "models": {},
              "blind_spots": blind, "news": None, "cases_read": []}
    if not found["incidents"]:
        return result
    incident = found["incidents"][0]
    desk = agents.Desk(gate, incident, found["unrelated"], collected["plant"], data["production"], briefing,
                       blind_spots=blind, cases=cases, case_id=case_id)

    def work(agent: str, task: str, tools: list) -> dict:
        run = run_agent(agent, model_of[agent], agents.system(agent, briefing), task, tools)
        result["runs"].append(run)
        result["models"][agent] = run["model"]
        return run

    first = work(FIRST, "The alarms of tonight have been joined into one incident. Take the office-side steps "
                 "that are justified.", desk.first_response_tools())
    plan = work(PLANNER, _task_planner(desk.first_steps), desk.planner_tools())["result"]
    late = collection.late(data)
    if plan and late:  # the night changes after the first plan
        news_started = time.monotonic()
        collected["alerts"] = sorted(collected["alerts"] + late, key=lambda a: (a["time"], a["id"]))
        found = correlation.correlate(gate, collected)
        incident = next(i for i in found["incidents"] if set(incident["alerts"]) <= set(i["alerts"]))
        desk.new_alarm(incident, late)
        desk.unrelated = found["unrelated"]
        before = {**plan, "priced": desk.stale[plan["recommended"]]}
        again = work(PLANNER, _task_planner(desk.first_steps) + " " + _task_news(plan, desk, late),
                     desk.planner_tools())["result"]
        result["news"] = {"alerts": late, "plan_before": before, "seconds_from_new_alarm": None}
        result["alerts"] = len(collected["alerts"])
        result["unrelated"] = found["unrelated"]
        if again:
            plan = again
        else:  # the planner did not plan again: nothing priced before the alarm may be offered as current
            plan = None
    first_plan, challenge = copy.deepcopy(plan), None
    for _ in range(briefing["debate"]["challenge_rounds"] if plan else 0):
        challenge = work(CHALLENGER, _task_challenger(plan, desk), desk.challenger_tools())["result"]
        if not challenge or challenge["verdict"] == "agree":
            break
        answer = work(PLANNER, _task_planner(desk.first_steps) + " " + _task_answer(challenge),
                      desk.planner_tools(answering=True))["result"]
        if not answer:
            break  # the planner did not answer: its first plan stands and the page says so
        plan = answer

    desk.price([])  # the decider always sees what doing nothing leaves open
    if plan is None:  # the planner failed: the page shows what the pricing tool alone knows
        for step in desk.steps:
            desk.price([step])
    shown = [k for k in (plan["options"] if plan else desk.priced) if k] + [""]
    if challenge and challenge["alternative"] and challenge["alternative"] not in shown:
        shown.insert(-1, challenge["alternative"])
    options = sorted((desk.priced[k] for k in shown), key=lambda o: (not o["points"], bool(open_lines(o)), o["cost_eur"]))
    # order on the page: responses that close every path, cheapest first; then the others; doing nothing last
    result.update({
        "incident": incident, "first_response": {"steps": desk.first_steps,
                                                 "left_alone": (first["result"] or {}).get("left_alone", "")},
        "first_plan": first_plan, "plan": plan, "challenge": challenge, "options": options,
        "recommended": desk.priced[plan["recommended"]]["points"] if plan else None,
        "priced_tonight": len(desk.priced), "held": []})
    if plan:
        result["held"] = response.request(gate, {"options": options, "recommended": result["recommended"],
                                                 "incident": f"{case_id}/{incident['id']}"}, collected["plant"])
    result["cases_read"] = desk.cases_read
    result["tokens"] = {k: sum(r["tokens"][k] for r in result["runs"]) for k in ("input", "output")}
    result["seconds_to_page"] = round(time.monotonic() - started, 2)
    if result["news"]:
        result["news"]["seconds_from_new_alarm"] = round(time.monotonic() - news_started, 2)
    result["page"] = decision.page(result)
    act(gate, "ot-briefing", "report.write", {"report": f"incident {incident['id']}, decision page",
                                              "characters": len(result["page"])})
    if cases is not None:
        cases.write(gate, case_memory.record(case_id, result))
    return result
