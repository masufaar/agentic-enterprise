"""Agent 3, impact and response: prices every way of containing the incident in lost
output, recommends one, and asks the Control Tower to carry it out.

The price of an option is the number of line-hours it stops, counted only while the
production schedule says the line would have been running, times the company's cost
of a stopped line-hour. Every input is an assumption stated in data/production.json
and data/plant.json; the arithmetic is the only thing this agent adds.

It also says what each option leaves open: the lines an intruder could still reach
from a device already under their control.

This agent is classified high-risk in the registry, so it may read on its own and
nothing else. Its isolation request is held for its accountable owner.
"""
from datetime import timedelta
from itertools import combinations

from . import act, load, tool_call_request, when

AGENT = "ot-response"


def _cuts(points: list[dict]) -> tuple[dict, dict]:
    """Zones and connections cut by these points, each with the longest hold in hours."""
    zones: dict[str, float] = {}
    links: dict[str, float] = {}
    for point in points:
        for zone in point.get("cuts_zones", []):
            zones[zone] = max(zones.get(zone, 0), point["hold_hours"])
        for link in point.get("cuts_connections", []):
            links[link] = max(links.get(link, 0), point["hold_hours"])
    return zones, links


def _running_hours(line_id: str, start, end, schedule: list[dict]) -> float:
    """Hours between start and end in which the line was planned to run."""
    hours = 0.0
    for slot in schedule:
        if slot["line"] == line_id and slot["state"] == "running":
            overlap = min(end, when(slot["to"])) - max(start, when(slot["from"]))
            hours += max(overlap.total_seconds(), 0) / 3600
    return hours


def _reachable_lines(incident: dict, plant: dict, cut_zones: dict, cut_links: dict) -> list[str]:
    """Lines an intruder can still reach from a foothold that is not itself disconnected."""
    edges: dict[str, set[str]] = {}
    for link in plant["connections"]:
        if link["id"] in cut_links:
            continue
        for other in (link["to"] if isinstance(link["to"], list) else [link["to"]]):
            edges.setdefault(link["from"], set()).add(other)
            edges.setdefault(other, set()).add(link["from"])
    seen = {z for z in incident["foothold_zones"] if z not in cut_zones}
    queue = list(seen)
    while queue:
        for nxt in edges.get(queue.pop(), ()):
            if nxt not in seen and nxt not in cut_zones:
                seen.add(nxt)
                queue.append(nxt)
    line_of = {z["id"]: z.get("line") for z in plant["zones"]}
    return sorted({line_of[z] for z in seen if line_of.get(z)})


def _name(points: list[dict]) -> str:
    names = [p["name"] for p in points]
    return " and ".join(names[:1] + [n[0].lower() + n[1:] for n in names[1:]]) or "Do nothing and keep watching"


def open_lines(option: dict) -> list[str]:
    """Lines not ruled out: within reach of a known foothold, or in a zone nobody watched tonight."""
    return sorted(set(option["lines_still_reachable"]) | set(option.get("lines_not_watched", [])))


def _not_watched(plant: dict, cut_zones: dict, unwatched_sides) -> list[str]:
    """Lines with a zone on a side whose monitoring sent nothing tonight, and that this response does not cut.
    Nobody can say whether the intruder is already there, so these lines are never counted as safe."""
    lines = {}
    for zone in plant["zones"]:
        if zone.get("line") and zone["side"] in unwatched_sides and zone["id"] not in cut_zones:
            lines[zone["line"]] = True
    return sorted(lines)


def price(points: list[dict], incident: dict, plant: dict, production: dict, unwatched_sides=()) -> dict:
    rate = production["cost_per_stopped_line_hour_eur"]
    buffer = production["assumptions"]["order_buffer_hours"]["value"]
    recovery = production["assumptions"]["recovery_hours_if_encrypted"]["value"]
    start = when(incident["last_seen"])
    cut_zones, cut_links = _cuts(points)
    lines, total = [], 0.0
    for line in production["lines"]:
        hold = max((cut_zones[c] for c in line["cells"] if c in cut_zones), default=0)
        if hold:  # a disconnected cell stops its whole line (assumption)
            why = "disconnected"
            hours = _running_hours(line["id"], start, start + timedelta(hours=hold), production["schedule"])
        elif production["orders_arrive_over"] in cut_links:
            why = "out of orders"  # runs on loaded orders first, then stops until the link reopens
            closed = cut_links[production["orders_arrive_over"]]
            hours = _running_hours(line["id"], start + timedelta(hours=min(buffer, closed)),
                                   start + timedelta(hours=closed), production["schedule"])
        else:
            why, hours = "", 0.0
        restart = line.get("restart_extra_hours", 0) if hours > 0 else 0
        if hours > 0:
            lines.append({"line": line["id"], "name": line["name"], "why": why, "hours_stopped": round(hours, 2),
                          "restart_hours": restart, "cost_eur": round((hours + restart) * rate)})
            total += (hours + restart) * rate
    reachable = _reachable_lines(incident, plant, cut_zones, cut_links)
    unseen = [l for l in _not_watched(plant, cut_zones, unwatched_sides) if l not in reachable]
    at_stake = sum((recovery + line.get("restart_extra_hours", 0)) * rate
                   for line in production["lines"] if line["id"] in reachable or line["id"] in unseen)
    return {"points": [p["id"] for p in points],
            "name": _name(points),
            "cost_eur": round(total), "lines_stopped": lines,
            "lines_still_reachable": reachable, "lines_not_watched": unseen, "still_at_stake_eur": round(at_stake)}


def _options(plant: dict) -> list[list[dict]]:
    """Every single isolation point, and every pair in which neither makes the other pointless."""
    points = plant["isolation_points"]
    covered = lambda p: set(p.get("cuts_zones", [])) | set(p.get("cuts_connections", []))
    pairs = [[a, b] for a, b in combinations(points, 2)
             if not covered(a) <= covered(b) and not covered(b) <= covered(a)]
    return [[]] + [[p] for p in points] + pairs


def assess(gateway, incident: dict, plant: dict) -> dict:
    act(gateway, AGENT, "incident.read", {"incident": incident["id"]})
    act(gateway, AGENT, "network.read", {"what": "plant layout", "plant": plant["plant"]["id"]})
    act(gateway, AGENT, "production.read", {"what": "schedule and cost of a stopped line-hour"})
    production = load("production.json")
    options = [price(points, incident, plant, production) for points in _options(plant)]
    closed = [o for o in options if not o["lines_still_reachable"]]
    # Cheapest option that leaves no line within reach; if none closes every path,
    # the one with the lowest cost plus what remains at stake.
    best = (min(closed, key=lambda o: (o["cost_eur"], len(o["points"]))) if closed
            else min(options, key=lambda o: o["cost_eur"] + o["still_at_stake_eur"]))
    return {"incident": incident["id"], "decided_at": incident["last_seen"], "options": options,
            "recommended": best["points"], "production": production}


def request(gateway, assessment: dict, plant: dict) -> list[dict]:
    """Ask for the recommended isolation. The gateway holds it; nothing is carried out here."""
    best = next(o for o in assessment["options"] if o["points"] == assessment["recommended"])
    names = {p["id"]: p for p in plant["isolation_points"]}
    verdicts = []
    for point in best["points"]:
        verdict = tool_call_request(gateway, {"agent_id": AGENT, "tool": "network.isolate", "input": {
            "isolation_point": point, "what": names[point]["name"], "plant": plant["plant"]["id"],
            "hold_hours": names[point]["hold_hours"], "incident": assessment["incident"],
            "expected_cost_of_whole_response_eur": best["cost_eur"]}})["verdict"]  # held: the answer is "ask"
        verdicts.append({"isolation_point": point, "what": names[point]["name"], **verdict})
    return verdicts
