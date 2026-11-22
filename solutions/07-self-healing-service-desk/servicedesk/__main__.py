"""Run from this solution folder. Everything here is fixed code: no model, no key.

  python -m servicedesk tickets              what the 200 synthetic tickets hold
  python -m servicedesk ladder               where each ticket type stands on the autonomy ladder
  python -m servicedesk try AGENT OPERATION TICKET [key=value ...]
                                             one call through the connector, for example:
                                             python -m servicedesk try sd-verifier resolve SD-26-0164
  python -m servicedesk generate             write the synthetic data again (same seed, same files)
"""
import json
import sys
from collections import Counter

from control_tower.gateway import Gateway

from . import Refused, load
from .connector import Connector
from .ladder import Ladder
from .suite import SuiteProblem


def tickets() -> str:
    all_tickets = load("tickets.json")["tickets"]
    types = load("ticket-types.json")["types"]
    closed = [t for t in all_tickets if t["state"] == "closed"]
    lines = [f"{len(all_tickets)} tickets: {len(closed)} closed, {len(all_tickets) - len(closed)} open.", "",
             f"{'type':<28}{'closed':>8}{'open':>6}  route"]
    for key, kind in types.items():
        mine = [t for t in all_tickets if t["type"] == key]
        done = sum(t["state"] == "closed" for t in mine)
        lines.append(f"{key:<28}{done:>8}{len(mine) - done:>6}  {kind['route']}")
    lines += ["", "Closed by:"] + [f"  {who:<28}{count:>4}" for who, count in Counter(t["closed_by"] for t in closed).most_common()]
    return "\n".join(lines)


def ladder() -> str:
    table = Ladder()
    lines = [f"{'ticket type':<28}{'rung':<16}{'ceiling':<16}{'checked':>8}  step up"]
    for row in table.table():
        lines.append(f"{row['type']:<28}{table.names[row['level']]:<16}{table.names[row['ceiling']]:<16}"
                     f"{row['checked_since_last_move']:>8}  "
                     f"{'ready: ' if row['ready_for_step_up'] else 'waits: '}{row['waits_for']}")
    lines.append(f"\nA step up is approved by the {table.decider}. A step down is immediate.")
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    command = argv[0] if argv else ""
    if command == "tickets":
        print(tickets())
    elif command == "ladder":
        print(ladder())
    elif command == "generate":
        from .generate import write
        print("Written: " + ", ".join(f"data/{name}" for name in write()))
    elif command == "try" and len(argv) >= 4:
        given = dict(a.split("=", 1) for a in argv[4:])
        try:
            out = Connector(Gateway()).call(argv[1], argv[2], ticket=argv[3], **given)
        except (Refused, SuiteProblem) as stopped:
            print(f"REFUSED  {stopped}")
            return 2
        print(json.dumps(out, indent=1))
    else:
        print(__doc__)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
