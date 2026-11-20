"""Items 3, 4 and 7 of the list of ten, and the word limits, on prepared replies.

  3  a night with one monitoring tool missing: the page names the blind spot, and the
     lines that tool would have watched are never priced as safe;
  4  a new alarm after the first plan: every price is out of date, the planner plans
     again, and the page shows the plan before and after;
  7  case memory: written after a night, read at the next, the person's note kept,
     and held steps found per case.

Like test_agents.py, these prove the harness, not the reasoning of a real model.
"""
import json

from sentinel import decision, load, night
from sentinel.agents import CHALLENGER, FIRST, PLANNER
from sentinel.cases import CaseBook
from sentinel.model import Scripted
from test_agents import (B2, LINK, OWNER, PLANT, GOOD_PLAN, OFFICE_STEPS, ask, asked, challenge, first_script,
                         gate, models, plan, planner_script, turn)  # noqa: F401 (gate is a fixture)

DOWN, NEWS = "plant-monitoring-down", "new-alarm-after-plan"
ALL_PRICES = ([], [B2], [LINK], [B2, LINK], [PLANT])


def option(result, steps):
    key = "+".join(steps)
    return next(o for o in result["options"] if "+".join(o["points"]) == key)


# -- item 3: one monitoring tool missing --------------------------------------
LINK_ONLY = plan([LINK], [[LINK], [PLANT]], why="Closing the link costs nothing tonight.",
                 open_="The plant floor is not watched tonight; the intruder may already be there.")


def test_a_missing_monitoring_tool_is_not_read_and_the_page_names_the_blind_spot(gate):
    result = night.run_night(models(planner=planner_script(LINK_ONLY)), gate, night=DOWN)
    reads = [r["params"].get("from") for r in gate.audit.records() if r["tool"] == "security.alerts.read"]
    assert "plant-floor-monitoring" not in reads and "office-security-monitoring" in reads
    assert result["incident"]["alerts"] == ["IT-1", "IT-2", "IT-3", "IT-4"]
    assert "**Blind spot tonight: the plant-floor-monitoring (simulated) on the plant floor sent nothing.**" in result["page"]
    assert "Nothing: the plant-floor-monitoring (simulated) sent no alarm tonight." in result["page"]


def test_without_the_plant_floor_tool_the_free_response_is_not_counted_as_safe(gate):
    result = night.run_night(models(planner=planner_script(LINK_ONLY)), gate, night=DOWN)
    link = option(result, [LINK])
    assert link["cost_eur"] == 0
    assert link["lines_still_reachable"] == []  # what the office alarms alone would say
    assert link["lines_not_watched"] == ["line-a", "line-b", "line-c"]  # what the harness says
    assert result["plan"]["closes_every_path"] is False
    assert option(result, [PLANT])["lines_not_watched"] == []
    assert "| Line A (not watched), Line B (not watched), Line C (not watched) |" in result["page"]
    assert "within reach or unwatched" in result["page"]


def test_on_a_blind_night_a_plan_that_says_nothing_about_what_remains_open_is_handed_back(gate):
    silent = plan([PLANT], [[PLANT], [LINK]], why="The whole plant floor is the only response that rules anything out.")
    fixed = plan([PLANT], [[PLANT], [LINK]], why="The whole plant floor is the only response that rules anything out.",
                 open_="Nothing is seen on the plant floor tonight; the cost is the price of not seeing.")
    result = night.run_night(models(planner=planner_script(silent, fixed)), gate, night=DOWN)
    refused = asked(result, PLANNER, "submit_plan")[0]
    assert refused["failed"] and "A monitoring tool sent nothing tonight" in refused["result"]
    assert result["plan"]["closes_every_path"] is True


def test_every_agent_is_told_which_monitoring_sent_nothing(gate):
    result = night.run_night(models(planner=planner_script(LINK_ONLY)), gate, night=DOWN)
    seen = asked(result, PLANNER, "read_incident")[0]["result"]
    assert seen["monitoring_that_sent_nothing_tonight"][0]["tool"] == "plant-floor-monitoring (simulated)"


# -- item 4: a new alarm after the first plan ---------------------------------
WIDER = plan([PLANT], [[PLANT], [B2, LINK]], why="The new alarm puts Line C within reach; only the whole plant floor closes it.")


def news_planner(*second):
    return planner_script(GOOD_PLAN) + [turn(*[ask("price_response", steps=s) for s in ([B2, LINK], [PLANT])]),
                                        *[turn(s) for s in second]]


def test_a_new_alarm_sends_the_planner_back_and_the_page_shows_the_plan_before_and_after(gate):
    result = night.run_night(models(planner=news_planner(WIDER)), gate, night=NEWS)
    planner_runs = [r for r in result["runs"] if r["agent"] == PLANNER]
    assert len(planner_runs) == 2
    assert result["news"]["plan_before"]["recommended"] == f"{B2}+{LINK}"
    assert result["recommended"] == [PLANT]
    assert "OT-5" in result["incident"]["alerts"] and "cell-c1" in result["incident"]["foothold_zones"]
    page = result["page"]
    assert "**The night changed after the first plan.** A new alarm arrived at 03:09 UTC." in page
    assert "Before it, the planner recommended Disconnect Line B, cell 2 and close the link" in page
    assert "## The plan before the new alarm" in page and "(new alarm, after the first plan)" in page
    assert "Time from the new alarm to this page:" in page
    assert option(result, [B2, LINK])["lines_still_reachable"] == ["line-c"]


def test_the_planner_is_told_what_arrived_and_that_every_price_is_out_of_date(gate):
    planner = Scripted(news_planner(WIDER))
    night.run_night({**models(), PLANNER: planner}, gate, night=NEWS)
    second_task = [a["turns"][0]["text"] for a in planner.asked if "A new alarm arrived" in a["turns"][0]["text"]]
    assert second_task and "03:09 UTC, hmi-c1 to plc-c1-01" in second_task[0]
    assert "every price made before is out of date" in second_task[0]


def test_a_plan_that_reuses_a_price_from_before_the_alarm_is_handed_back(gate):
    stale = plan([PLANT], [[PLANT], [B2]], why="Line C is now within reach.")  # [B2] was priced before the alarm only
    script = news_planner(stale, WIDER)
    result = night.run_night(models(planner=script), gate, night=NEWS)
    refused = [a for a in asked(result, PLANNER, "submit_plan") if a["failed"]][0]
    assert "was priced before the new alarm. Price it again." in refused["result"]
    assert result["recommended"] == [PLANT]


def test_a_planner_that_does_not_plan_again_leaves_no_out_of_date_recommendation(gate):
    script = planner_script(GOOD_PLAN) + [turn(text="I cannot.")] * 12
    result = night.run_night(models(planner=script), gate, night=NEWS)
    assert result["plan"] is None and result["recommended"] is None and result["held"] == []
    assert "**The planner agent did not hand in a plan.**" in result["page"]


# -- item 7: case memory --------------------------------------------------------
def test_a_night_is_written_to_the_case_memory_and_the_decision_and_note_are_added(gate, tmp_path):
    book = CaseBook(tmp_path / "cases")
    result = night.run_night(models(), gate, cases=book)
    assert result["case"] == "CASE-001"
    case = book.get("CASE-001")
    assert case["status"] == "waiting for decision" and case["recommended"]["lost_output_eur"] == 120000
    assert "jump-p04-01" in case["devices"] and "svc-maint-p04" in case["accounts"]
    decision.decide(gate, result, 1, OWNER, note="Check the Line C panel before choosing cell 2 again.", cases=book)
    case = book.get("CASE-001")
    assert case["status"] == "decided" and case["decision"]["by"] == OWNER and case["decision"]["recommended"]
    assert case["note_by_decider"] == "Check the Line C panel before choosing cell 2 again."
    writes = [r for r in gate.audit.records() if r["tool"] == "cases.write"]
    assert [(w["agent_id"], w["decision"]) for w in writes] == [("ot-briefing", "allow")] * 2
    assert "This night is recorded as CASE-001." in result["page"]


def test_the_next_night_reads_the_earlier_case_through_the_control_tower(gate, tmp_path):
    book = CaseBook(tmp_path / "cases")
    first = night.run_night(models(), gate, cases=book)
    decision.decide(gate, first, 1, OWNER, note="Check the Line C panel before choosing cell 2 again.", cases=book)
    reading = [turn(ask("read_cases"))] + planner_script(GOOD_PLAN)
    second = night.run_night(models(planner=reading), gate, cases=book)
    found = asked(second, PLANNER, "read_cases")[0]["result"]["earlier_cases_sharing_a_device_or_account"]
    assert [c["case"] for c in found] == ["CASE-001"]
    assert found[0]["note_by_decider"] == "Check the Line C panel before choosing cell 2 again."
    assert "jump-p04-01" in found[0]["shared_with_tonight"]
    assert second["case"] == "CASE-002" and second["cases_read"] == ["CASE-001"]
    assert "Earlier cases read by the agents: CASE-001." in second["page"]
    read = [r for r in gate.audit.records() if r["tool"] == "cases.read"]
    assert read and read[0]["agent_id"] == PLANNER and read[0]["decision"] == "allow"


def test_a_night_does_not_read_its_own_case_or_later_ones(gate, tmp_path):
    book = CaseBook(tmp_path / "cases")
    result = night.run_night(models(planner=[turn(ask("read_cases"))] + planner_script(GOOD_PLAN)), gate, cases=book)
    assert asked(result, PLANNER, "read_cases")[0]["result"]["earlier_cases_sharing_a_device_or_account"] == []


def test_the_first_response_agent_cannot_read_cases(gate):
    assert gate.check(FIRST, "cases.read", {})["decision"] == "deny"
    assert gate.check(CHALLENGER, "cases.read", {})["decision"] == "allow"
    assert gate.check(CHALLENGER, "cases.write", {})["decision"] == "deny"


def test_held_steps_are_found_per_case_so_two_nights_in_one_record_do_not_mix(gate, tmp_path):
    book = CaseBook(tmp_path / "cases")
    first = night.run_night(models(), gate, cases=book)
    second = night.run_night(models(), gate, cases=book)
    decision.decide(gate, second, 1, OWNER, cases=book)
    released = [r for r in gate.audit.records() if r["tool"] == "network.isolate" and r.get("approved_by") == OWNER]
    assert released and all(r["params"]["incident"] == "CASE-002/INC-001" for r in released)
    from control_tower.approvals import Approvals
    still = [i for i in Approvals(gate).pending() if i["request"].get("incident") == "CASE-001/INC-001"]
    assert len(still) == 2  # the first night's held steps wait for their own decision
    assert first["case"] == "CASE-001"


def test_a_proposed_briefing_change_is_recorded_and_shown_but_not_applied(gate, tmp_path):
    book = CaseBook(tmp_path / "cases")
    before = json.dumps(load("briefing.json"))
    proposing = plan([B2, LINK], [[B2, LINK], [PLANT], [B2]], why="Cheapest response that leaves no line within reach.",
                     open_="Line C panel not checked.")
    proposing["input"]["proposed_briefing_change"] = "Name the Line C maintenance crew as a safety call in every plan."
    result = night.run_night(models(planner=planner_script(proposing)), gate, cases=book)
    assert book.get("CASE-001")["proposed_briefing_change"].startswith("Name the Line C maintenance crew")
    assert "## A change to the company briefing, proposed by the planner" in result["page"]
    assert "Not applied: a person decides whether the briefing changes." in result["page"]
    assert json.dumps(load("briefing.json")) == before


# -- word limits ----------------------------------------------------------------
def test_a_hand_in_over_the_word_limit_is_handed_back_and_shortened(gate):
    long_left = "word " * 80
    script = first_script(*OFFICE_STEPS, left=long_left) + [turn(ask("report_first_response", left_alone="The engineering workstation."))]
    result = night.run_night(models(first=script), gate)
    reports = asked(result, FIRST, "report_first_response")
    assert reports[0]["failed"] and "'left_alone' has 80 words; the limit is 60" in reports[0]["result"]
    assert result["first_response"]["left_alone"] == "The engineering workstation."


def test_every_agent_is_told_the_word_limits_and_how_to_write_figures(gate):
    agents_models = models()
    night.run_night(agents_models, gate)
    for agent, model in agents_models.items():
        assert "Word limits for what you hand in: left_alone 60 words" in model.asked[0]["system"]
    assert "EUR 120,000" in agents_models[PLANNER].asked[0]["system"]
