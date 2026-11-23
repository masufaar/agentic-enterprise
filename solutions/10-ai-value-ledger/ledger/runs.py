"""The measured side: what the agents of this repository actually used.

Every solution that has run with a real model records each run under
reports/runs/*.json: which agents ran, how long it took and how many tokens it
used. The ledger reads those files. Nothing here is typed in by hand; if a
solution has never run, it has no measured cost and the ledger says so.

Most solutions record one use per file: one night of the Sentinel is one file. A
solution whose agents work one ticket per run records several agent runs in one
file, each with its own tokens, under "runs". For those, the ledger reads the agent
runs one by one and prices a unit of work made of a stated number of runs per agent
(see per_unit). Only reports/runs/ is read: red-team records are kept elsewhere on
purpose, because an attack is not a unit of work.

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


def agent_runs(solution: str) -> dict:
    """The individual agent runs inside the records of one solution, per agent.
    Only records that list their runs one by one under 'runs' are read."""
    folder = SOLUTIONS / solution / "reports" / "runs"
    per_agent: dict[str, dict] = {}
    for path in sorted(folder.glob("*.json")) if folder.exists() else []:
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        for run in record.get("runs") or []:
            if not isinstance(run, dict) or "agent" not in run or "tokens" not in run:
                continue
            seen = per_agent.setdefault(run["agent"], {"runs": 0, "tokens": {"input": 0, "output": 0},
                                                       "models": set(), "files": []})
            seen["runs"] += 1
            for side in ("input", "output"):
                seen["tokens"][side] += run["tokens"][side]
            seen["models"].add(run.get("model") or record.get("models", {}).get(run["agent"], ""))
            name = f"{solution}/reports/runs/{path.name}"
            if name not in seen["files"]:
                seen["files"].append(name)
    return per_agent


def per_unit(solution: str, runs_per_unit: dict) -> dict | None:
    """The measured tokens of one unit of work: for each agent, its average tokens per run
    times the runs it takes per unit, added up. None if an agent of the unit never ran."""
    found = agent_runs(solution)
    if not all(found.get(agent, {}).get("runs") for agent in runs_per_unit):
        return None
    tokens = {side: sum(found[a]["tokens"][side] / found[a]["runs"] * share for a, share in runs_per_unit.items())
              for side in ("input", "output")}
    models = sorted({m.split(",")[0].strip() for a in runs_per_unit for m in found[a]["models"]})
    files = sorted({f for a in runs_per_unit for f in found[a]["files"]})
    return {"tokens": {side: round(v) for side, v in tokens.items()},
            "model": models[0] if len(models) == 1 else ", ".join(models),
            "agents": {a: {"runs": found[a]["runs"], "tokens": found[a]["tokens"],
                           "tokens_per_run": {s: round(found[a]["tokens"][s] / found[a]["runs"]) for s in ("input", "output")},
                           "per_unit": share} for a, share in runs_per_unit.items()},
            "runs": sum(found[a]["runs"] for a in runs_per_unit), "files": files}
