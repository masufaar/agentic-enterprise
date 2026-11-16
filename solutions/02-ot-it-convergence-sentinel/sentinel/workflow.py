"""The four agents in order. Each one acts only through the Control Tower gateway."""
from control_tower.gateway import Gateway

from . import REPORTS
from . import briefing, collection, correlation, response


def run(gateway: Gateway | None = None, write: bool = True) -> dict:
    gateway = gateway if gateway is not None else Gateway()
    collected = collection.collect(gateway)
    found = correlation.correlate(gateway, collected)
    result = {"alerts": collected["alerts"], "incidents": found["incidents"],
              "unrelated": found["unrelated"], "assessments": [], "held": [], "pages": []}
    for incident in found["incidents"]:
        assessment = response.assess(gateway, incident, collected["plant"])
        held = response.request(gateway, assessment, collected["plant"])
        text = briefing.brief(gateway, incident, assessment, held, found["unrelated"], collected["plant"])
        result["assessments"].append(assessment)
        result["held"] += held
        result["pages"].append(text)
    if write and result["pages"]:
        REPORTS.mkdir(exist_ok=True)
        (REPORTS / "incident-latest.md").write_text(result["pages"][-1], encoding="utf-8")
    return result
