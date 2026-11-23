"""Run from this solution folder. Everything here is fixed code: no model, no key.

  python -m servicedesk tickets              what the 200 synthetic tickets hold
  python -m servicedesk ladder               where each ticket type stands on the autonomy ladder
  python -m servicedesk try AGENT OPERATION TICKET [key=value ...]
                                             one call through the connector, for example:
                                             python -m servicedesk try sd-verifier resolve SD-26-0164
  python -m servicedesk generate             write the synthetic data again (same seed, same files)

  python -m servicedesk sample               the three scenarios with prepared replies in place of a model;
                                             writes reports/samples. Shows the fixed code, proves nothing about a model.

  python -m servicedesk redteam              the red team against the resolution agent, every attack assumed to
                                             have succeeded in taking the agent over; writes reports/redteam-latest

The two agents, with a real model:

  python -m servicedesk scenarios            what scenarios exist
  python -m servicedesk run [SCENARIO] [--record]
                                             the verifier and the resolution agent on one scenario; writes the page.
                                             Needs HALDEN_MODEL_KEY_FILE (path of a file holding the model key).
                                             Optional: HALDEN_MODEL, HALDEN_EFFORT. --record keeps the run in reports/.
  python -m servicedesk runs [--record]      every scenario, one after the other
  python -m servicedesk redteam --live [--record]
                                             the same attack tickets given to the resolution agent on a real model
"""
import json
import os
import sys
from collections import Counter
from datetime import date

from control_tower.gateway import Gateway

from . import REPORTS, Refused, load
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
    elif command == "scenarios":
        from .session import load_scenario, scenarios
        for name in scenarios():
            print(f"{name:<20}{load_scenario(name)['title']}")
    elif command == "sample":
        import tempfile
        from pathlib import Path
        from harness.model import Scripted
        from .prepared import REPLIES
        from .session import run_scenario
        (REPORTS / "samples").mkdir(parents=True, exist_ok=True)
        for name, replies in REPLIES.items():
            result = run_scenario(Scripted(replies), name, folder=Path(tempfile.mkdtemp()))
            result["seconds_to_page"] = 0.0   # so that the sample is the same file every time
            from .page import page
            (REPORTS / "samples" / f"{name}-scripted.md").write_text(page(result), encoding="utf-8")
            print(f"Written: reports/samples/{name}-scripted.md")
    elif command == "redteam":
        from . import redteam
        if "--live" in argv:
            from harness.model import Claude, ModelError
            model = Claude(model=os.environ.get("HALDEN_MODEL", "claude-fable-5-2"),
                           effort=os.environ.get("HALDEN_EFFORT", "medium"))
            print("Red team, live: 20 tickets, one agent run each. Several minutes; nothing is printed until it ends.", flush=True)
            try:
                report = redteam.run(model)
            except (ModelError, Refused) as stopped:
                print(f"Stopped: {stopped}")
                return 2
            if "--record" in argv:
                (REPORTS / "redteam").mkdir(parents=True, exist_ok=True)
                stem = redteam.publish(report, f"redteam/live-{date.today().isoformat()}-{model.model}", keep=True)
                print(f"Recorded: reports/{stem}.md and .json")
        else:
            report = redteam.run()
            redteam.publish(report)
        print(json.dumps(report["summary"], indent=1))
        for r in report["results"]:
            print(f"  {r['id']:<9}{r['outcome']:<14}{', '.join(sorted({x['by'] for x in r['stopped']}))}")
    elif command in ("run", "runs"):
        return run(command, argv)
    else:
        print(__doc__)
        return 1
    return 0


def run(command: str, argv: list[str]) -> int:
    from harness.model import Claude, ModelError
    from .session import DEFAULT_SCENARIO, run_scenario, scenarios
    names = [a for a in argv[1:] if not a.startswith("--")]
    wanted = [names[0] if names else DEFAULT_SCENARIO] if command == "run" else scenarios()
    model = Claude(model=os.environ.get("HALDEN_MODEL", "claude-fable-5-2"),
                   effort=os.environ.get("HALDEN_EFFORT", "medium"))
    for scenario in wanted:
        print(f"Scenario: {scenario}. A few minutes; nothing is printed until it ends.", flush=True)
        try:
            result = run_scenario(model, scenario)
        except (ModelError, Refused) as stopped:
            print(f"Stopped: {stopped}")
            return 2
        if command == "run":
            print(result["page"])
        else:
            print(f"  Done in {result['seconds_to_page']} seconds: {len(result['findings'])} findings, "
                  f"{sum(s['step'] == 'work' for s in result['steps'])} tickets worked.")
        if "--record" in argv:
            runs = REPORTS / "runs"
            runs.mkdir(parents=True, exist_ok=True)
            stem = f"{scenario}-{date.today().isoformat()}-{model.model}"
            for letter in "bcdefgh":            # an earlier record of the same day is kept, never overwritten
                if not (runs / f"{stem}.json").exists():
                    break
                stem = f"{stem.split('-run-')[0]}-run-{letter}"
            (runs / f"{stem}.json").write_text(json.dumps(result, indent=1), encoding="utf-8")
            (runs / f"{stem}.md").write_text(result["page"], encoding="utf-8")
            print(f"  Recorded: reports/runs/{stem}.md and .json")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
