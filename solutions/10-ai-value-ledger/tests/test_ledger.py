"""The ledger: fixed code, no model. What it must get right, and what it must refuse to guess."""
import pytest

from ledger import load
from ledger.ledger import amounts, build, grade, trend
from ledger.prices import PriceError, Prices
from ledger.runs import measured, records

PORTFOLIO = load("portfolio.json")
MEASUREMENTS = PORTFOLIO["measurements"]


# -- prices ------------------------------------------------------------------
def test_price_table_carries_its_date_and_source():
    prices = Prices()
    assert prices.as_read_on == "2026-11-20"
    assert "platform.claude.com" in prices.source


def test_cost_of_a_run_is_the_published_price():
    prices = Prices()
    # 1m input and 100k output on Fable 5.2: 8 USD + 4 USD
    assert prices.usd({"input": 1_000_000, "output": 100_000}, "claude-fable-5-2") == 12.0
    assert prices.eur({"input": 1_000_000, "output": 100_000}, "claude-fable-5-2") == 12.0 * 0.92


def test_a_cheap_model_at_high_volume_is_not_rounded_down_to_nothing():
    """Found by the analyst agent in the first real run: a run costing a tenth of a cent was
    rounded to zero before being multiplied by 46,000 runs, and a whole year priced at zero."""
    prices = Prices()
    per_run = prices.eur({"input": 9000, "output": 700}, "claude-haiku-5-5")
    assert 0 < per_run < 0.01
    assert round(per_run * 46000) == 53


def test_the_effort_setting_is_not_part_of_the_price():
    prices = Prices()
    assert prices.model_name("claude-fable-5-2, effort medium") == "claude-fable-5-2"


def test_an_unpriced_model_stops_the_ledger_rather_than_being_guessed():
    with pytest.raises(PriceError):
        Prices().eur({"input": 1, "output": 1}, "some-other-model")


# -- the measured side -------------------------------------------------------
def test_the_sentinel_runs_in_this_repository_are_read():
    found = measured("02-ot-it-convergence-sentinel", "ot-response")
    assert found and found["runs"] == len(records("02-ot-it-convergence-sentinel"))
    assert found["tokens"]["input"] > 0 and found["tokens"]["output"] > 0
    assert all(f.endswith(".json") for f in found["files"])


def test_a_solution_that_never_ran_has_no_measured_cost():
    assert measured("06-portfolio-truth-agent") is None


# -- the grade ---------------------------------------------------------------
def test_a_claim_with_a_measurement_record_is_measured():
    claim = {"value_eur": 611000, "stated_by": "Head of IT Operations",
             "measurement": {"record": "service-desk-2026-q3", "value_eur": 611000}}
    assert grade(claim, MEASUREMENTS)["grade"] == "measured"


def test_a_claim_naming_a_record_that_does_not_exist_is_only_a_claim():
    claim = {"value_eur": 500000, "stated_by": "A sponsor", "measurement": {"record": "not-a-record"}}
    graded = grade(claim, MEASUREMENTS)
    assert graded["grade"] == "claimed" and "does not exist" in graded["why"]


def test_a_formula_with_its_assumptions_is_calculated_and_is_recomputed():
    claim = {"value_eur": 999999, "stated_by": "A sponsor", "formula": "a * b",
             "assumptions": {"a": 2, "b": 400000}}
    graded = grade(claim, MEASUREMENTS)
    assert graded["grade"] == "calculated"
    assert graded["value_eur"] == 800000      # the formula wins over the stated figure
    assert "The formula wins" in graded["why"]


def test_a_figure_with_neither_record_nor_formula_is_claimed():
    assert grade({"value_eur": 1200000, "stated_by": "Head of Quality"}, MEASUREMENTS)["grade"] == "claimed"


# -- the lines ---------------------------------------------------------------
def test_the_sentinel_line_has_a_measured_cost_and_names_the_records():
    line = next(l for l in build(scenario={"agents": ["ot-response"]})["lines"] if l["agent"] == "ot-response")
    assert line["cost"]["basis"] == "measured"
    assert line["cost"]["evidence"]["files"]
    assert "upper bound" in line["cost"]["evidence"]["note"]
    assert line["benefit"]["grade"] == "calculated"     # EUR 800,000 is an assumption, and says so


def test_benefits_are_totalled_by_grade_and_never_across_grades():
    built = build({"agents": ["sd-resolution", "quality-traceability", "ot-response"]})
    totals = built["totals_by_grade"]
    assert totals["measured"]["agents"] == ["sd-resolution"]
    assert totals["claimed"]["agents"] == ["quality-traceability"]
    assert totals["calculated"]["agents"] == ["ot-response"]
    assert "total_benefit_eur" not in built      # there is no one number for benefit, on purpose


def test_a_scenario_may_change_a_value_without_changing_the_portfolio_file():
    base = build({"agents": ["disruption-monitor"]})["lines"][0]["cost"]["eur_per_run"]
    changed = build({"agents": ["disruption-monitor"],
                     "changes": {"disruption-monitor": {"cost": {"tokens_per_run": {"input": 86000, "output": 2400}}}}}
                    )["lines"][0]["cost"]["eur_per_run"]
    assert changed > base
    assert load("portfolio.json")["agents"][3]["cost"]["tokens_per_run"]["input"] == 31000   # file untouched


def test_an_agent_that_is_not_in_the_portfolio_is_refused():
    with pytest.raises(KeyError):
        build({"agents": ["no-such-agent"]})


# -- cost against use --------------------------------------------------------
def test_cost_growing_faster_than_use_is_flagged():
    months = next(a for a in PORTFOLIO["agents"] if a["id"] == "disruption-monitor")["cost"]
    found = trend(months)
    assert found["cost_grows_faster_than_use"] is True
    assert found["use_change_pct"] < 5 and found["cost_per_run_change_pct"] > 100


def test_an_agent_without_months_has_no_trend():
    assert trend({"tokens_per_run": {"input": 1, "output": 1}}) is None


# -- what an agent may write -------------------------------------------------
def test_every_figure_an_agent_may_write_comes_from_the_ledger():
    built = build({"agents": ["sd-resolution", "ot-response"]})
    known = amounts(built)
    assert built["lines"][0]["benefit"]["value_eur"] in known
    assert built["cost_eur"] in known
    assert 123456 not in known


# -- the service desk line: cost per verified resolution ---------------------
def _service_desk_line():
    return build({"agents": ["sd-resolution"]})["lines"][0]


def test_the_service_desk_is_priced_per_verified_resolution_from_its_agent_runs():
    """Solution 07 records several agent runs per file. The unit is one resolution run and one
    verifier check, measured from the individual runs, not one file."""
    import json
    from ledger import SOLUTIONS
    folder = SOLUTIONS / "07-self-healing-service-desk" / "reports" / "runs"
    runs = [r for p in sorted(folder.glob("*.json")) for r in json.loads(p.read_text(encoding="utf-8"))["runs"]]
    average = {a: {s: sum(r["tokens"][s] for r in runs if r["agent"] == a) / sum(r["agent"] == a for r in runs)
                   for s in ("input", "output")} for a in ("sd-resolution", "sd-verifier")}
    line = _service_desk_line()
    cost = line["cost"]
    assert cost["basis"] == "measured" and cost["unit"] == "verified resolution"
    assert cost["evidence"]["runs_recorded"] == len(runs)
    for side in ("input", "output"):
        assert cost["tokens_per_run"][side] == round(average["sd-resolution"][side] + average["sd-verifier"][side])
    assert "upper bound" in cost["evidence"]["note"]


def test_red_team_records_are_not_a_unit_of_work():
    files = _service_desk_line()["cost"]["evidence"]["files"]
    assert files and all("/reports/runs/" in f for f in files)
    assert not any("redteam" in f for f in files)


def test_a_unit_whose_agent_never_ran_is_not_measured():
    from ledger.runs import per_unit
    assert per_unit("07-self-healing-service-desk", {"sd-resolution": 1, "no-such-agent": 1}) is None


def test_checking_a_sample_costs_less_than_checking_every_closure():
    every = _service_desk_line()["cost"]["eur_per_run"]
    sampled = build({"agents": ["sd-resolution"], "changes": {"sd-resolution": {"cost": {"unit": {
        "runs_per_unit": {"sd-resolution": 1, "sd-verifier": 0.2}}}}}})["lines"][0]["cost"]["eur_per_run"]
    assert sampled < every


def test_the_owner_in_the_ledger_is_the_owner_on_the_registry_cards():
    import json
    from ledger import CONTROL_TOWER
    cards = json.loads((CONTROL_TOWER / "data" / "agents.json").read_text(encoding="utf-8"))
    cards = cards if isinstance(cards, list) else cards.get("agents", list(cards.values()))
    owners = {c["id"]: c["owner"] for c in cards if isinstance(c, dict) and c.get("id", "").startswith("sd-")}
    line = _service_desk_line()
    assert owners["sd-resolution"] == owners["sd-verifier"] == line["owner"] == line["benefit"]["stated_by"]


def test_the_page_says_what_the_service_desk_measurement_does_not_show():
    from ledger.board import page
    built = build({"agents": ["sd-resolution"]})
    written = page({"ledger": built, "note": None, "decides": "Chief AI Officer", "analyst": "no agent ran",
                    "runs": [], "read": [], "build_hour_eur": built["build_hour_eur"],
                    "tokens": {"input": 0, "output": 0}, "seconds_to_page": 0.0})
    assert "a verified resolution on claude-fable-5-2" in written
    assert "not tickets whose fix held" in written
