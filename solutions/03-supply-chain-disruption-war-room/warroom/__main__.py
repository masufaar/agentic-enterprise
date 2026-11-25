"""Run from this solution folder. Everything here is fixed code: no model, no key.

  python -m warroom overview             what the synthetic data holds
  python -m warroom ladder               where each response action type stands on the autonomy ladder
  python -m warroom trace KIND ID        the bill-of-materials walk, e.g. trace supplier SUP-NORD
  python -m warroom generate             write the synthetic data again (same seed, same files)

  python -m warroom sample               the scenarios with prepared replies in place of a model;
                                         writes reports/samples. Shows the fixed code, proves nothing about a model.

  python -m warroom redteam              the red team against the two agents, every agent assumed taken over;
                                         writes reports/redteam-latest

The two agents, with a real model:

  python -m warroom scenarios            what scenarios exist
  python -m warroom run [SCENARIO] [--record]
                                         the monitor and the sourcing agent on one scenario; writes the page.
                                         Needs HALDEN_MODEL_KEY_FILE (path of a file holding the model key).
                                         Optional: HALDEN_MODEL, HALDEN_EFFORT. --record keeps the run in reports/.
  python -m warroom runs [--record]      every scenario, one after the other
  python -m warroom redteam --live [--record]
                                         the same attacks given to the agents on a real model
"""
import json
import os
import sys
from datetime import date

from . import REPORTS, Refused, load
from .connector import Connector
from .ladder import Ladder
from .systems import SystemProblem


def overview() -> str:
    parts = load("parts.json")
    orders = load("orders.json")
    events = load("events.json")
    lines = [f"Halden Industrial, synthetic data as of {parts['as_of']}.", "",
             f"{len(parts['parts'])} parts, {len(parts['products'])} products, "
             f"{len(load('suppliers.json')['suppliers'])} suppliers.",
             f"{len(orders['customer_orders'])} open customer orders, {len(orders['purchase_orders'])} open POs.",
             f"{len(events['events'])} events on the feed.", "",
             "Single-source parts:"]
    for pid, p in parts["parts"].items():
        if p["single_source"]:
            lines.append(f"  {pid} ({p['name']}) from {p['primary_supplier']}")
    lines += ["", "Events on the feed:"]
    for e in events["events"]:
        lines.append(f"  {e['id']}  {e['date']}  {e['type']:<14}{'verified' if e['verified'] else 'UNVERIFIED':<10}  {e['headline']}")
    return "\n".join(lines)


def ladder() -> str:
    table = Ladder()
    lines = [f"{'action type':<22}{'rung':<16}{'ceiling':<16}{'cases':>6}  step up"]
    for row in table.table():
        lines.append(f"{row['type']:<22}{table.names[row['level']]:<16}{table.names[row['ceiling']]:<16}"
                     f"{row['cases_since_last_move']:>6}  {'ready: ' if row['ready_for_step_up'] else ''}{row['waits_for']}")
    lines.append(f"\nA step up is approved by the {table.decider}. A step down is immediate.")
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    command = argv[0] if argv else ""
    if command == "overview":
        print(overview())
    elif command == "ladder":
        print(ladder())
    elif command == "trace" and len(argv) >= 3:
        from control_tower.gateway import Gateway
        from . import MONITOR
        try:
            out = Connector(Gateway()).call(MONITOR, "trace_exposure", kind=argv[1], id=argv[2])
        except (Refused, SystemProblem) as stopped:
            print(f"REFUSED  {stopped}")
            return 2
        print(json.dumps(out, indent=1, ensure_ascii=False))
    elif command == "generate":
        from .generate import write
        print("Written: " + ", ".join(f"data/{name}" for name in write()))
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
            result["seconds_to_page"] = 0.0
            from .page import page
            (REPORTS / "samples" / f"{name}-scripted.md").write_text(page(result), encoding="utf-8")
            print(f"Written: reports/samples/{name}-scripted.md")
    elif command == "redteam":
        from . import redteam
        if "--live" in argv:
            from harness.model import Claude, ModelError
            model = Claude(model=os.environ.get("HALDEN_MODEL", "claude-fable-5-2"),
                           effort=os.environ.get("HALDEN_EFFORT", "medium"))
            print("Red team, live: the attacks given to the agents on a real model. Several minutes.", flush=True)
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
            print(f"  Done in {result['seconds_to_page']} seconds.")
        if "--record" in argv:
            runs = REPORTS / "runs"
            runs.mkdir(parents=True, exist_ok=True)
            stem = f"{scenario}-{date.today().isoformat()}-{model.model}"
            for letter in "bcdefgh":
                if not (runs / f"{stem}.json").exists():
                    break
                stem = f"{stem.split('-run-')[0]}-run-{letter}"
            (runs / f"{stem}.json").write_text(json.dumps(result, indent=1, ensure_ascii=False), encoding="utf-8")
            (runs / f"{stem}.md").write_text(result["page"], encoding="utf-8")
            print(f"  Recorded: reports/runs/{stem}.md and .json")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
