"""Agent 2, correlation: decides which alerts belong together.

Two alerts are linked when they are at most LINK_MINUTES apart and name the same
device or the same account. Linked alerts form a group. A group is an incident
when it holds more than one alert and either reaches from the office side to the
plant floor or contains an alert of the highest severity. Everything else is
reported as unrelated, so nothing is dropped silently.
"""
from . import act, when

AGENT = "ot-threat-correlation"
LINK_MINUTES = 60
GENERIC_ACCOUNTS = {None, "system"}  # shared by everything, so they link nothing


def _names(alert: dict) -> set[str]:
    names = {alert["origin"], alert["target"]}
    if alert["account"] not in GENERIC_ACCOUNTS:
        names.add(alert["account"])
    return names


def _groups(alerts: list[dict]) -> list[list[dict]]:
    parent = list(range(len(alerts)))

    def root(i: int) -> int:
        while parent[i] != i:
            i = parent[i]
        return i

    for i, a in enumerate(alerts):
        for j in range(i):
            b = alerts[j]
            near = abs((when(a["time"]) - when(b["time"])).total_seconds()) <= LINK_MINUTES * 60
            if near and _names(a) & _names(b):
                parent[root(i)] = root(j)
    groups: dict[int, list[dict]] = {}
    for i, alert in enumerate(alerts):
        groups.setdefault(root(i), []).append(alert)
    return list(groups.values())


def _incident(number: int, alerts: list[dict], plant: dict) -> dict:
    zone_of = {a["id"]: a["zone"] for a in plant["assets"]}
    line_of = {z["id"]: z.get("line") for z in plant["zones"]}
    path: list[str] = []
    for alert in alerts:
        for device in (alert["origin"], alert["target"]):
            if device not in path:
                path.append(device)
    # A foothold is a device the intruder acted from against another device.
    footholds = [d for d in path if any(a["origin"] == d and a["target"] != d for a in alerts)]
    zones = [z for z in dict.fromkeys(zone_of.get(d) for d in path) if z]
    return {
        "id": f"INC-{number:03d}", "alerts": [a["id"] for a in alerts],
        "first_seen": alerts[0]["time"], "last_seen": alerts[-1]["time"],
        "sides": sorted({a["side"] for a in alerts}), "path": path, "footholds": footholds,
        "foothold_zones": [z for z in dict.fromkeys(zone_of.get(d) for d in footholds) if z],
        "zones": zones, "lines_touched": sorted({line_of[z] for z in zones if line_of.get(z)}),
        "accounts": sorted({a["account"] for a in alerts if a["account"] not in GENERIC_ACCOUNTS}),
        "accounts_moved": sorted({a["account"] for a in alerts if a["account"] not in GENERIC_ACCOUNTS
                                  and a["origin"] != a["target"]}),
        "timeline": [{"id": a["id"], "time": a["time"], "side": a["side"], "text": a["text"],
                      "origin": a["origin"], "target": a["target"]} for a in alerts],
    }


def correlate(gateway, collected: dict) -> dict:
    act(gateway, AGENT, "security.alerts.read", {"from": "collection agent", "alerts": len(collected["alerts"])})
    act(gateway, AGENT, "network.read", {"what": "plant layout", "plant": collected["plant"]["plant"]["id"]})
    incidents, unrelated = [], []
    for group in _groups(collected["alerts"]):
        crosses = {a["side"] for a in group} == {"office", "plant"}
        if len(group) > 1 and (crosses or max(a["severity"] for a in group) >= 4):
            incidents.append(_incident(len(incidents) + 1, group, collected["plant"]))
        else:
            unrelated += group
    for incident in incidents:
        act(gateway, AGENT, "incident.write", {"incident": incident["id"], "alerts": incident["alerts"]})
    return {"incidents": incidents,
            "unrelated": [{"id": a["id"], "text": a["text"]} for a in unrelated]}
