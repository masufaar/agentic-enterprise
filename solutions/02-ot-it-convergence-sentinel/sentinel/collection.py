"""Agent 1, collection: reads the plant layout and the alerts of the two tools the
company already owns, and puts every alert into one format.

The two tools name things differently (data/events_office.json, data/events_plant.json).
After this step an alert looks the same wherever it came from.
"""
from . import act, load

AGENT = "ot-asset-discovery"
OFFICE_SEVERITY = {"info": 1, "low": 2, "medium": 3, "high": 4}


def _from_office(alert: dict, tool: str) -> dict:
    return {"id": alert["id"], "time": alert["time"], "tool": tool, "side": "office",
            "origin": alert.get("source_host", alert["host"]), "target": alert["host"],
            "account": alert.get("account"), "kind": alert["type"],
            "severity": OFFICE_SEVERITY[alert["severity"]], "text": alert["detail"]}


def _from_plant(event: dict, tool: str) -> dict:
    return {"id": event["event_id"], "time": event["ts"], "tool": tool, "side": "plant",
            "origin": event["src"], "target": event["dst"], "account": None,
            "kind": event["category"], "severity": event["level"], "text": event["description"]}


def collect(gateway, night: dict | None = None) -> dict:
    """'night' replaces the scripted data files with another night (see sentinel/night.py)."""
    night = night or {}
    act(gateway, AGENT, "network.read", {"what": "plant layout", "plant": "plant-04"})
    plant = night.get("plant") or load("plant.json")
    act(gateway, AGENT, "security.alerts.read", {"from": "office-security-monitoring"})
    office = night.get("office") or load("events_office.json")
    act(gateway, AGENT, "security.alerts.read", {"from": "plant-floor-monitoring"})
    floor = night.get("floor") or load("events_plant.json")
    alerts = ([_from_office(a, office["source_tool"]) for a in office["alerts"]]
              + [_from_plant(e, floor["sensor"]) for e in floor["events"]])
    return {"plant": plant, "alerts": sorted(alerts, key=lambda a: (a["time"], a["id"]))}
