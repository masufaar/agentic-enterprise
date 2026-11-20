"""The measured side: what the agents of this repository actually used.

Every solution that has run with a real model records each run under
reports/runs/*.json: which agents ran, how long it took and how many tokens it
used. The ledger reads those files. Nothing here is typed in by hand; if a
solution has never run, it has no measured cost and the ledger says so.

A warning the ledger carries onto every line built from these records: the model
connector counts cache reads inside the input total, and cache reads are cheaper
than fresh input. A cost computed from these records is therefore an upper bound.
"""
import json

from . import SOLUTIONS


def records(solution: str) -> list[dict]:
    """Every recorded run of one solution, oldest file name first."""
    folder = SOLUTIONS / solution / "reports" / "runs"
    found = []
    for path in sorted(folder.glob("*.json")) if folder.exists() else []:
        try:
            run = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if "tokens" in run and "models" in run:
            found.append({"file": f"{solution}/reports/runs/{path.name}", "tokens": run["tokens"],
                          "models": sorted(set(run["models"].values())), "seconds": run.get("seconds_to_page"),
                          "agents": sorted(run["models"])})
    return found


def measured(solution: str, agent: str | None = None) -> dict | None:
    """The measured cost side of one solution: tokens, runs, models and the files behind them.
    With 'agent', only the runs in which that agent took part. None if nothing has run."""
    found = [r for r in records(solution) if agent is None or agent in r["agents"]]
    if not found:
        return None
    models = sorted({m for r in found for m in r["models"]})
    return {"runs": len(found),
            "tokens": {side: sum(r["tokens"][side] for r in found) for side in ("input", "output")},
            "models": models, "model": models[0] if len(models) == 1 else ", ".join(models),
            "seconds_total": round(sum(r["seconds"] or 0 for r in found), 2),
            "files": [r["file"] for r in found]}
