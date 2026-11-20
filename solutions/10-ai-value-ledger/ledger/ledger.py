"""The ledger itself: one line per agent, in fixed code.

A line has two sides and they are never mixed:

  cost     what the agent used. Measured when it comes from run records in this
           repository, assumed when it comes from a figure in the portfolio file.
           Model cost plus the build effort, both shown.
  benefit  what someone says the agent returns, with the grade of the evidence
           behind it. The grade is worked out here, from the evidence that exists:

             measured    the claim names a measurement record, and that record is
                         in the portfolio's list of measurements
             calculated  the claim has a formula and assumptions that are written
                         down, and the formula produces the figure stated
             claimed     neither of those: a figure from the person who asked for
                         the budget

No sponsor can type in a grade, and no agent can argue one upwards. A total is made
per grade and never across grades: a measured euro and a claimed euro are not the
same money.

The ledger also watches cost per use over time, where the portfolio has months. An
agent whose cost per run grows while its use does not is flagged, because that is
the pattern a board only notices when the invoice arrives.
"""
from . import load
from .prices import Prices
from .runs import measured

GRADES = ("measured", "calculated", "claimed")


def _formula_value(claim: dict) -> float | None:
    """Multiply the assumptions named in the formula. Only 'a * b * c' and division by a
    number are understood; anything else is not a formula the ledger can check."""
    formula, assumptions = claim.get("formula"), claim.get("assumptions") or {}
    if not formula:
        return None
    value = 1.0
    for part in formula.replace(" ", "").split("*"):
        for piece, divide in [(p, i > 0) for i, p in enumerate(part.split("/"))]:
            if piece in assumptions:
                number = assumptions[piece]
            else:
                try:
                    number = float(piece)
                except ValueError:
                    return None
            value = value / number if divide else value * number
    return round(value, 2)


def grade(claim: dict, measurements: dict) -> dict:
    """The grade of one benefit claim, and why it has that grade."""
    record = (claim.get("measurement") or {}).get("record")
    if record and record in measurements:
        held = measurements[record]
        return {"grade": "measured", "why": f"Measured: {held['method']} ({held['system']}, {held['period']}).",
                "record": record, "value_eur": claim["measurement"].get("value_eur", claim["value_eur"])}
    if record:
        return {"grade": "claimed", "record": record, "value_eur": claim["value_eur"],
                "why": f"The claim names the measurement record '{record}', and that record does not exist. "
                       "Until it does, this is a claim."}
    computed = _formula_value(claim)
    if computed is not None:
        stated = claim["value_eur"]
        agrees = abs(computed - stated) < 1
        named = " x ".join(f"{k} {v:,}" for k, v in (claim.get("assumptions") or {}).items())
        return {"grade": "calculated", "record": None, "value_eur": round(computed),
                "why": f"Calculated from stated assumptions: {named}." if agrees else
                       f"Calculated from stated assumptions: {named}. The claim states "
                       f"{stated:,.0f}; the formula gives {computed:,.0f}. The formula wins."}
    return {"grade": "claimed", "record": None, "value_eur": claim["value_eur"],
            "why": "No measurement record and no formula: the figure is the sponsor's statement. "
                   + (claim.get("note") or "")}


def trend(cost: dict) -> dict | None:
    """Cost per run over the months the portfolio holds, if it holds any."""
    months = cost.get("months")
    if not months or len(months) < 2:
        return None
    per_run = [{"month": m["month"], "runs": m["runs"], "cost_eur": m["cost_eur"],
                "cost_per_run_eur": round(m["cost_eur"] / m["runs"], 3)} for m in months]
    first, last = per_run[0], per_run[-1]
    use_change = (last["runs"] - first["runs"]) / first["runs"]
    cost_change = (last["cost_per_run_eur"] - first["cost_per_run_eur"]) / first["cost_per_run_eur"]
    return {"months": per_run, "first": first["month"], "last": last["month"],
            "use_change_pct": round(use_change * 100, 1), "cost_per_run_change_pct": round(cost_change * 100, 1),
            "cost_grows_faster_than_use": cost_change > 0.2 and cost_change > use_change + 0.2,
            "note": cost.get("months_note", "")}


def line(entry: dict, prices: Prices, portfolio: dict) -> dict:
    """One agent: what it cost, what is claimed for it, and how good that claim is."""
    cost, hour = entry["cost"], portfolio["build_hour_eur"]
    runs_a_year = cost["runs_per_year"]
    seen = measured(cost["from_run_records"], entry["id"]) if cost.get("from_run_records") else None
    if seen:
        per_run_tokens = {side: round(seen["tokens"][side] / seen["runs"]) for side in ("input", "output")}
        model, basis = seen["model"], "measured"
        evidence = {"runs_recorded": seen["runs"], "files": seen["files"],
                    "note": "Measured from the run records of this repository. Cache reads are counted at the "
                            "full input price, so this is an upper bound."}
    else:
        per_run_tokens, model, basis = cost["tokens_per_run"], cost["model"], "assumed"
        evidence = {"runs_recorded": 0, "files": [],
                    "note": "No run records: the tokens per run are an assumption from the portfolio file."}
    per_run_eur = prices.eur(per_run_tokens, model)
    model_cost = round(per_run_eur * runs_a_year)
    build_cost = round(cost["build_hours"] * hour)
    graded = grade(entry["claim"], portfolio.get("measurements", {}))
    benefit = graded["value_eur"]
    return {
        "agent": entry["id"], "name": entry["name"], "solution": entry["solution"], "owner": entry["owner"],
        "state_in_the_company": entry.get("state_in_the_company", "not stated"),
        "cost": {"model": model, "basis": basis, "tokens_per_run": per_run_tokens, "eur_per_run": per_run_eur,
                 "runs_per_year": runs_a_year, "runs_per_year_basis": cost.get("runs_per_year_basis", "assumption"),
                 "model_eur_per_year": model_cost, "build_hours": cost["build_hours"], "build_eur": build_cost,
                 "total_first_year_eur": model_cost + build_cost, "evidence": evidence},
        "benefit": {"value_eur": benefit, "grade": graded["grade"], "why": graded["why"].strip(),
                    "record": graded["record"], "stated_by": entry["claim"]["stated_by"],
                    "as_claimed_eur": entry["claim"]["value_eur"], "source": entry["claim"].get("source")},
        "net_first_year_eur": round(benefit - model_cost - build_cost),
        "trend": trend(cost),
    }


def build(scenario: dict | None = None, portfolio: dict | None = None, prices: Prices | None = None) -> dict:
    """The ledger for one scenario: its lines, and the totals held apart by grade."""
    portfolio = portfolio if portfolio is not None else load("portfolio.json")
    prices = prices if prices is not None else Prices()
    entries = {e["id"]: e for e in portfolio["agents"]}
    wanted = scenario.get("agents") if scenario else list(entries)
    changes = (scenario or {}).get("changes", {})
    lines = []
    for agent_id in wanted:
        if agent_id not in entries:
            raise KeyError(f"{agent_id} is not in the portfolio")
        entry = _merge(entries[agent_id], changes.get(agent_id, {}))
        lines.append(line(entry, prices, portfolio))
    totals = {g: {"benefit_eur": sum(l["benefit"]["value_eur"] for l in lines if l["benefit"]["grade"] == g),
                  "agents": [l["agent"] for l in lines if l["benefit"]["grade"] == g]} for g in GRADES}
    return {"title": (scenario or {}).get("title", "The whole portfolio"),
            "question": (scenario or {}).get("question", ""),
            "lines": lines, "totals_by_grade": totals,
            "cost_eur": sum(l["cost"]["total_first_year_eur"] for l in lines),
            "cost_measured_eur": sum(l["cost"]["total_first_year_eur"] for l in lines if l["cost"]["basis"] == "measured"),
            "prices": {"as_read_on": prices.as_read_on, "source": prices.source,
                       "eur_per_usd": prices.eur_per_usd},
            "build_hour_eur": portfolio["build_hour_eur"], "year": portfolio["year"]}


def _merge(entry: dict, change: dict) -> dict:
    """A scenario changes a few values of an entry; everything else stays as it is."""
    merged = dict(entry)
    for key, value in change.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def amounts(ledger: dict) -> set[int]:
    """Every euro figure the ledger produced. An agent may write no other."""
    known = {ledger["cost_eur"], ledger["cost_measured_eur"], ledger["build_hour_eur"]}
    for total in ledger["totals_by_grade"].values():
        known.add(total["benefit_eur"])
    for l in ledger["lines"]:
        cost = l["cost"]
        known |= {cost["model_eur_per_year"], cost["build_eur"], cost["total_first_year_eur"],
                  l["benefit"]["value_eur"], l["benefit"]["as_claimed_eur"], abs(l["net_first_year_eur"])}
        if l["trend"]:
            known |= {m["cost_eur"] for m in l["trend"]["months"]}
    return {int(round(a)) for a in known}
