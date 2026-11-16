"""Run from this solution folder:

  python -m sentinel run        the four agents on the scripted incident; writes reports/incident-latest.md
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


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
