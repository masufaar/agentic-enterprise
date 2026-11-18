"""Run from this solution folder:

  python -m sentinel run        the rule-based first version on the scripted incident (no model); writes reports/incident-latest.md
  python -m sentinel night [NAME] [--record]
                                the agents on one night, with a real model; writes the decision page.
                                Needs SENTINEL_MODEL_KEY_FILE (path of a file holding the model key).
                                Optional: SENTINEL_MODEL, SENTINEL_EFFORT. --record keeps the run in reports/.
  python -m sentinel decide NUMBER --as "Head of OT Security"
                                the named person chooses a response of the last night
  python -m sentinel waiting    isolation requests waiting for a named person
  python -m sentinel release --as "Head of OT Security"
                                release the waiting isolation requests in that role (simulated network)
"""
import sys

from . import Refused
from .briefing import eur
from .workflow import run


def main(argv: list[str]) -> int:
    from control_tower.approvals import ApprovalError, Approvals
    from control_tower.gateway import Gateway
    command = argv[0] if argv else ""
    if command == "run":
        try:
            result = run()
        except Refused as refused:
            print(f"Stopped by the Control Tower: {refused}")
            return 2
        print(f"Alerts collected: {len(result['alerts'])}. Incidents: {len(result['incidents'])}. "
              f"Unrelated alerts: {len(result['unrelated'])}.")
        for assessment in result["assessments"]:
            for option in assessment["options"]:
                mark = "  <- recommended" if option["points"] == assessment["recommended"] else ""
                print(f"  {eur(option['cost_eur']):>12}  {option['name']}{mark}")
        for held in result["held"]:
            print(f"  {held['decision']}: {held['what']} (rules {held['rule']})")
        print("Written: reports/incident-latest.md")
        return 0
    if command in ("night", "decide"):
        return _agents(command, argv[1:])
    if command in ("waiting", "release"):
        approvals = Approvals(Gateway())
        mine = [i for i in approvals.pending() if i["agent_id"] == "ot-response"]
        if command == "waiting":
            for item in mine:
                print(f"Item {item['seq']}: {item['request'].get('what')} - waiting for {item['approver']}")
            print(f"{len(mine)} waiting.")
            return 0
        if "--as" not in argv:
            print('State the role: --as "Head of OT Security"')
            return 1
        role = argv[argv.index("--as") + 1]
        for item in mine:
            try:
                verdict = approvals.release(item["seq"], role)
                print(f"Item {item['seq']}: {verdict['decision']} ({verdict['reason']})")
            except ApprovalError as error:
                print(f"Item {item['seq']}: not released. {error}")
        return 0
    print(__doc__)
    return 1


def _agents(command: str, argv: list[str]) -> int:
    import json
    import os
    from datetime import date
    from control_tower.approvals import ApprovalError
    from . import REPORTS, ROOT, decision, night
    from .model import Claude, ModelError
    last = ROOT / "state" / "last-night.json"
    if command == "night":
        name = next((a for a in argv if not a.startswith("--")), night.DEFAULT_NIGHT)
        model = Claude(model=os.environ.get("SENTINEL_MODEL", "claude-fable-5-2"),
                       effort=os.environ.get("SENTINEL_EFFORT", "medium"))
        try:
            result = night.run_night(model, night=name)
        except (ModelError, Refused) as stopped:
            print(f"Stopped: {stopped}")
            return 2
        if result["incident"] is None:
            print("No incident tonight: no group of alarms reached from the office side to the plant floor.")
            return 0
        last.parent.mkdir(exist_ok=True)
        last.write_text(json.dumps(result), encoding="utf-8")
        print(result["page"])
        if "--record" in argv:
            runs = REPORTS / "runs"
            runs.mkdir(parents=True, exist_ok=True)
            stem = f"{name}-{date.today().isoformat()}-{model.model}"
            (runs / f"{stem}.json").write_text(json.dumps(result, indent=1), encoding="utf-8")
            (runs / f"{stem}.md").write_text(result["page"], encoding="utf-8")
            print(f"Recorded: reports/runs/{stem}.md and .json")
        return 0
    if "--as" not in argv or not argv or not argv[0].isdigit() or not last.exists():
        print('After a night: python -m sentinel decide NUMBER --as "Head of OT Security"')
        return 1
    try:
        outcome = decision.decide(night.gateway(), json.loads(last.read_text(encoding="utf-8")),
                                  int(argv[0]), argv[argv.index("--as") + 1])
    except ApprovalError as error:
        print(f"Not decided. {error}")
        return 1
    print(f"Chosen: {outcome['chosen']['name']} ({eur(outcome['chosen']['cost_eur'])} in lost output).")
    for step in outcome["carried_out"]:
        print(f"  {step['what']}: {step['decision']}, carried out (simulated): {step['executed']}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
