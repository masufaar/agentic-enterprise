"""Run from this solution folder:

  python -m ledger ledger [SCENARIO]      the ledger alone, fixed code, no model: one line per agent
  python -m ledger review [SCENARIO] [--record]
                                          the analyst agent on that ledger, with a real model; writes the page.
                                          Needs HALDEN_MODEL_KEY_FILE (path of a file holding the model key).
                                          Optional: HALDEN_MODEL, HALDEN_EFFORT. --record keeps the run in reports/.
  python -m ledger reviews [--record]     every scenario in data/scenarios, one after the other
  python -m ledger scenarios              what scenarios exist

Scenarios: pays-back, benefit-without-evidence, cost-growing.
"""
import json
import os
import sys
from datetime import date

from . import DATA, REPORTS, Refused, eur
from .ledger import build
from .model import Claude, ModelError
from .review import DEFAULT_SCENARIO, load_scenario, run_review

GRADE = {"measured": "measured", "calculated": "calculated", "claimed": "claimed only"}


def _print_ledger(built: dict) -> None:
    print(built["title"])
    print(f"{'agent':<24}{'cost (first year)':>20}{'benefit':>16}  evidence")
    for line in built["lines"]:
        print(f"{line['agent']:<24}{eur(line['cost']['total_first_year_eur']):>20}"
              f"{eur(line['benefit']['value_eur']):>16}  {GRADE[line['benefit']['grade']]}"
              f" ({line['cost']['basis']} cost)")
    print(f"\nFirst-year cost: {eur(built['cost_eur'])}, of which {eur(built['cost_measured_eur'])} measured.")
    for grade, total in built["totals_by_grade"].items():
        if total["agents"]:
            print(f"Benefit {GRADE[grade]}: {eur(total['benefit_eur'])}")
    print("Benefits of different grades are never added together.")


def main(argv: list[str]) -> int:
    command = argv[0] if argv else ""
    names = [a for a in argv[1:] if not a.startswith("--")]
    if command == "scenarios":
        for path in sorted((DATA / "scenarios").glob("*.json")):
            print(f"{path.stem:<28}{json.loads(path.read_text(encoding='utf-8'))['title']}")
        return 0
    if command == "ledger":
        scenario = names[0] if names else DEFAULT_SCENARIO
        built = build(load_scenario(scenario))
        _print_ledger(built)
        if "--write" in argv:   # the page as fixed code alone produces it, with no agent and no model
            from .board import page
            from .review import gateway
            written = page({"ledger": built, "note": None, "decides": "Chief AI Officer",
                            "answers_for_the_agent": gateway().registry["value-ledger"]["owner"],
                            "analyst": "no agent ran", "runs": [], "read": [],
                            "build_hour_eur": built["build_hour_eur"],
                            "tokens": {"input": 0, "output": 0}, "seconds_to_page": 0.0})
            REPORTS.mkdir(parents=True, exist_ok=True)
            (REPORTS / "ledger-latest.md").write_text(written, encoding="utf-8")
            print("Written: reports/ledger-latest.md")
        return 0
    if command in ("review", "reviews"):
        if command == "review":
            wanted = [names[0] if names else DEFAULT_SCENARIO]
        else:
            wanted = sorted(p.stem for p in (DATA / "scenarios").glob("*.json"))
        model = Claude(model=os.environ.get("HALDEN_MODEL", "claude-fable-5-2"),
                       effort=os.environ.get("HALDEN_EFFORT", "medium"))
        for scenario in wanted:
            print(f"Review: {scenario}. Under a minute; nothing is printed until it ends.", flush=True)
            try:
                result = run_review(model, scenario=scenario)
            except (ModelError, Refused) as stopped:
                print(f"Stopped: {stopped}")
                return 2
            if command == "review":
                print(result["page"])
            else:
                verdicts = ", ".join(f"{v['agent']}: {v['verdict']}" for v in (result["note"] or {}).get("verdicts", []))
                print(f"  Done in {result['seconds_to_page']} seconds. {verdicts or 'no note accepted'}")
            if "--record" in argv:
                runs = REPORTS / "runs"
                runs.mkdir(parents=True, exist_ok=True)
                stem = f"{scenario}-{date.today().isoformat()}-{model.model}"
                (runs / f"{stem}.json").write_text(json.dumps(result, indent=1), encoding="utf-8")
                (runs / f"{stem}.md").write_text(result["page"], encoding="utf-8")
                print(f"  Recorded: reports/runs/{stem}.md and .json")
        return 0
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
