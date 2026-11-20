"""The analyst agent: what the harness refuses to accept from it, and what the page shows.

Every test here runs on the scripted stand-in, so the suite runs without a key and
without cost. What is tested is the fixed code around the model: the controls.
"""
import pytest

from control_tower.gateway import Gateway
from ledger import ANALYST, load
from ledger.analyst import Desk, system
from ledger.ledger import build
from ledger.loop import ToolProblem
from ledger.model import Scripted
from ledger.review import run_review

BRIEFING = load("briefing.json")


def desk(agents=("sd-resolution", "quality-traceability", "disruption-monitor")) -> Desk:
    gate = Gateway()
    return Desk(gate, build({"agents": list(agents)}), BRIEFING, registry=gate.registry)


def note(**over) -> dict:
    given = {"verdicts": [{"agent": "sd-resolution", "verdict": "fund", "reason": "Measured over 13 weeks."},
                          {"agent": "quality-traceability", "verdict": "build the evidence",
                           "reason": "No measurement was ever set up."},
                          {"agent": "disruption-monitor", "verdict": "build the evidence",
                           "reason": "Its cost per run has nearly tripled."}],
             "for_the_board": "The supply chain monitor costs more every month for the same number of runs.",
             "what_to_measure_first": "Disruptions caught early, counted against the quarter before the agent.",
             "what_nobody_knows": "Whether a caught disruption would have been caught by a person anyway."}
    given.update(over)
    return given


# -- what the agent is told --------------------------------------------------
def test_the_briefing_tells_the_agent_what_the_grades_mean_and_who_decides():
    text = system(BRIEFING)
    assert "measured" in text and "claimed" in text
    assert "Chief AI Officer" in text
    assert "decides nothing" in text


# -- the hand-in checks ------------------------------------------------------
def test_a_note_that_follows_the_rules_is_accepted():
    accepted = desk().submit(note())
    assert [v["agent"] for v in accepted["verdicts"]] == ["sd-resolution", "quality-traceability", "disruption-monitor"]
    assert accepted["verdicts"][0]["grade"] == "measured"


def test_an_agent_whose_benefit_is_only_claimed_cannot_be_recommended_for_funding():
    given = note(verdicts=[{"agent": "sd-resolution", "verdict": "fund", "reason": "Measured."},
                           {"agent": "quality-traceability", "verdict": "fund", "reason": "The sponsor is sure."},
                           {"agent": "disruption-monitor", "verdict": "stop", "reason": "Cost is running away."}])
    with pytest.raises(ToolProblem) as refused:
        desk().submit(given)
    assert "only claimed" in str(refused.value)


def test_an_agent_that_costs_more_than_it_returns_cannot_be_recommended_for_funding():
    one = desk(agents=["portfolio-truth"])
    one.lines["portfolio-truth"]["net_first_year_eur"] = -5000
    with pytest.raises(ToolProblem) as refused:
        one.submit({"verdicts": [{"agent": "portfolio-truth", "verdict": "fund", "reason": "It feels useful."}],
                    "for_the_board": "One agent reviewed.", "what_to_measure_first": "Hours saved."})
    assert "costs more than it returns" in str(refused.value)


def test_every_agent_in_the_ledger_needs_a_verdict():
    given = note(verdicts=[{"agent": "sd-resolution", "verdict": "fund", "reason": "Measured."}])
    with pytest.raises(ToolProblem) as refused:
        desk().submit(given)
    assert "Missing" in str(refused.value)


def test_an_agent_outside_the_ledger_cannot_be_given_a_verdict():
    given = note(verdicts=note()["verdicts"] + [{"agent": "ot-response", "verdict": "stop", "reason": "No."}])
    with pytest.raises(ToolProblem) as refused:
        desk().submit(given)
    assert "not an agent in this ledger" in str(refused.value)


def test_an_agent_whose_cost_outruns_its_use_must_be_named_to_the_board():
    given = note(for_the_board="Two agents are fine and one needs work.")
    with pytest.raises(ToolProblem) as refused:
        desk().submit(given)
    assert "growing faster than its use" in str(refused.value)


def test_a_euro_figure_the_ledger_did_not_produce_is_refused():
    given = note(for_the_board="The supply chain monitor saves EUR 999,999 a year.")
    with pytest.raises(ToolProblem) as refused:
        desk().submit(given)
    assert "did not come from a tool" in str(refused.value)


def test_a_text_over_the_word_limit_is_refused():
    given = note(what_to_measure_first="word " * 200)
    with pytest.raises(ToolProblem) as refused:
        desk().submit(given)
    assert "the limit is" in str(refused.value)


# -- the tools ---------------------------------------------------------------
def test_the_tools_read_only_and_go_through_the_control_tower():
    tools = {t.name: t for t in desk().tools()}
    assert set(tools) == {"read_portfolio", "read_cost", "read_claim", "read_trend", "submit_note"}
    out = tools["read_portfolio"].run({})
    assert out["totals_by_grade_eur"]["claimed"] > 0
    assert out["agents"][0]["state_in_the_control_tower"]


def test_asking_for_an_agent_outside_the_ledger_is_a_tool_problem_not_a_crash():
    tools = {t.name: t for t in desk().tools()}
    with pytest.raises(ToolProblem):
        tools["read_cost"].run({"agent": "ot-response"})


def test_a_trend_is_only_offered_where_months_were_recorded():
    tools = {t.name: t for t in desk().tools()}
    assert tools["read_trend"].run({"agent": "disruption-monitor"})["cost_grows_faster_than_use"] is True
    with pytest.raises(ToolProblem):
        tools["read_trend"].run({"agent": "sd-resolution"})


# -- one whole review --------------------------------------------------------
def scripted_review(scenario="cost-growing", **over):
    replies = [{"tool_calls": [{"id": "1", "name": "read_portfolio", "input": {}}]},
               {"tool_calls": [{"id": "2", "name": "read_trend", "input": {"agent": "disruption-monitor"}}]},
               {"text": "Note follows.",
                "tool_calls": [{"id": "3", "name": "submit_note", "input": note(**over)}]}]
    return run_review(Scripted(replies), scenario=scenario)


def test_a_whole_review_writes_a_page_with_the_grades_apart():
    result = scripted_review()
    assert result["runs"][0]["ended"] == "handed in"
    page = result["page"]
    assert "Benefit, held apart by the evidence behind it, never added together" in page
    assert "Measured:" in page and "Claimed only:" in page
    assert "the analyst's words" in page
    assert result["flagged"] == ["disruption-monitor"]


def test_the_page_says_where_every_figure_comes_from():
    page = scripted_review()["page"]
    assert "platform.claude.com" in page            # the price table and its date
    assert "assumption" in page                     # the euro rate and the run counts
    assert "upper bound" not in page or "run records" in page


def test_a_note_the_harness_refuses_leaves_the_ledger_standing():
    """The model hands in a note that breaks a rule, runs out of turns, and the page still
    shows the ledger: fixed code does not depend on the agent."""
    bad = {"verdicts": [{"agent": "disruption-monitor", "verdict": "fund", "reason": "It feels useful."}],
           "for_the_board": "All fine.", "what_to_measure_first": "Something."}
    replies = [{"text": "Note follows.", "tool_calls": [{"id": "1", "name": "submit_note", "input": bad}]}] * 12
    result = run_review(Scripted(replies), scenario="cost-growing")
    assert result["note"] is None
    assert "did not hand in a note that the harness accepted" in result["page"]
    assert "| Supply chain disruption monitor |" in result["page"]


def test_the_review_refuses_to_run_if_the_registry_lets_this_agent_act():
    gate = Gateway()
    gate.registry[ANALYST] = {**gate.registry[ANALYST], "autonomy": "act"}
    with pytest.raises(ValueError) as refused:
        run_review(Scripted([]), gate=gate, scenario="pays-back")
    assert "decides nothing" in str(refused.value)
