"""The agent loop, the three agents, the decision page and the decision.

Every test here runs on the scripted stand-in: prepared replies, no model. So these
tests prove the harness: that the loop hands failures back, that the controls hold
whatever a model asks for, that the page shows only priced figures, that only the
named person can decide. They do not prove that a real model reasons well. That is
what the recorded real runs are for.
"""
import copy
import json

import pytest

from sentinel import decision, load, night  # importing sentinel puts the Control Tower on the path
from control_tower.approvals import ApprovalError
from control_tower.audit import AuditLog
from control_tower.gateway import Gateway
from control_tower.killswitch import KillSwitch
from sentinel.agents import CHALLENGER, FIRST, PLANNER
from sentinel.loop import Tool, ToolProblem, run_agent
from sentinel.model import Scripted

B2, LINK, PLANT = "cut-cell-b2", "cut-link-dmz-ot", "cut-plant-ot"
OWNER = "Head of OT Security"
count = iter(range(10_000))


def ask(tool, **given):
    return {"id": f"c{next(count)}", "name": tool, "input": given}


def turn(*calls, text=""):
    return {"text": text, "tool_calls": list(calls)}


# -- prepared replies ---------------------------------------------------------
def first_script(*steps, left="The engineering workstation: it is on the plant floor."):
    return [turn(ask("read_incident"), ask("read_plant")), turn(*steps),
            turn(ask("report_first_response", left_alone=left))] if steps else \
           [turn(ask("read_incident")), turn(ask("report_first_response", left_alone=left))]


OFFICE_STEPS = (ask("suspend_account", account="svc-maint-p04"), ask("quarantine_workstation", device="ws-fin-117"),
                ask("close_remote_session", device="jump-p04-01"))


def plan(recommended, options, why="Cheapest response that leaves no line within reach.", open_="", answer=None):
    given = {"options": options, "recommended": recommended, "why": why, "what_remains_open": open_}
    if answer is not None:
        given["answer_to_challenger"] = answer
    return ask("submit_plan", **given)


def planner_script(*submissions, price=([], [B2], [LINK], [B2, LINK], [PLANT])):
    return [turn(ask("read_incident"), ask("read_plant"), ask("read_production")),
            turn(*[ask("price_response", steps=s) for s in price]), *[turn(s) for s in submissions]]


GOOD_PLAN = plan([B2, LINK], [[B2, LINK], [PLANT], [B2]])


def challenge(verdict="agree", argument="Checked the prices of all three responses; found nothing cheaper that is as safe.",
              alternative=None, price=([B2],)):
    given = {"verdict": verdict, "argument": argument, "what_nobody_knows": "Whether other cells are already touched."}
    if alternative is not None:
        given["alternative"] = alternative
    return [turn(*[ask("price_response", steps=s) for s in price]), turn(ask("submit_challenge", **given))]


def models(first=None, planner=None, challenger=None):
    return {FIRST: Scripted(first if first is not None else first_script(*OFFICE_STEPS)),
            PLANNER: Scripted(planner if planner is not None else planner_script(GOOD_PLAN)),
            CHALLENGER: Scripted(challenger if challenger is not None else challenge())}


@pytest.fixture
def gate(tmp_path):
    return night.gateway(audit=AuditLog(tmp_path / "audit.jsonl"), killswitch=KillSwitch(tmp_path / "kill.json"))


def asked(result, agent, tool):
    return [a for run in result["runs"] if run["agent"] == agent for step in run["steps"]
            for a in step["asked"] if a["tool"] == tool]


# -- the loop -----------------------------------------------------------------
def _toy_tools(log):
    def fragile(given):
        if given["n"] < 0:
            raise ToolProblem("n must not be negative")
        log.append(given["n"])
        return {"double": given["n"] * 2}
    return [Tool("double", "Doubles n.", fragile, {"n": {"type": "integer"}}),
            Tool("hand_in", "Hand in.", lambda g: {"answer": g["answer"]}, {"answer": {"type": "integer"}}, hand_in=True)]


def test_a_failed_tool_is_told_to_the_model_which_then_corrects_itself():
    log, model = [], Scripted([turn(ask("double", n=-1)), turn(ask("double", n=4)), turn(ask("hand_in", answer=8))])
    run = run_agent("toy", model, "s", "double four", _toy_tools(log))
    assert run["ended"] == "handed in" and run["result"] == {"answer": 8} and run["turns"] == 3 and log == [4]
    assert run["steps"][0]["asked"][0]["failed"] and "negative" in run["steps"][0]["asked"][0]["result"]
    told = model.asked[1]["turns"][-1]["results"][0]
    assert told["is_error"] and "negative" in told["content"]


def test_an_unknown_tool_and_a_wrong_input_are_handed_back_not_crashed_on():
    model = Scripted([turn(ask("delete_everything")), turn(ask("double", number=4)), turn(ask("hand_in", answer=0))])
    run = run_agent("toy", model, "s", "t", _toy_tools([]))
    assert [s["asked"][0]["failed"] for s in run["steps"]] == [True, True, False] and run["ended"] == "handed in"


def test_an_agent_that_stops_without_handing_in_is_reminded():
    model = Scripted([turn(text="I think the answer is 8."), turn(ask("hand_in", answer=8))])
    run = run_agent("toy", model, "s", "t", _toy_tools([]))
    assert run["steps"][0]["reminded"] and run["ended"] == "handed in"
    assert "not handed in" in model.asked[1]["turns"][-1]["text"]


def test_the_loop_ends_after_its_turns_and_says_so():
    model = Scripted([turn(ask("double", n=1))] * 3)
    run = run_agent("toy", model, "s", "t", _toy_tools([]), max_turns=3)
    assert run["ended"] == "out of turns" and run["result"] is None


def test_a_model_that_is_cut_off_or_refuses_ends_the_loop_without_a_result():
    for stop, ended in (("limit", "cut off"), ("refused", "refused by the model")):
        run = run_agent("toy", Scripted([{"text": "", "stop": stop}]), "s", "t", _toy_tools([]))
        assert run["ended"] == ended and run["result"] is None


# -- the scripted night -------------------------------------------------------
def test_a_night_ends_in_a_decision_page_with_a_recommendation_and_a_verdict(gate):
    result = night.run_night(models(), gate)
    page = result["page"]
    assert [r["agent"] for r in result["runs"]] == [FIRST, PLANNER, CHALLENGER]
    assert all(r["ended"] == "handed in" for r in result["runs"])
    assert result["recommended"] == [B2, LINK]
    assert "The planner recommends: Disconnect Line B, cell 2 and close the link" in page
    assert "EUR 120,000" in page and "The challenger agrees." in page
    assert f"the choice is with the {OWNER}" in page and "scripted stand-in (no model)" in page
    assert "(recommended)" in page and "Do nothing and keep watching" in page


def test_the_first_response_agent_takes_office_side_steps_on_its_own(gate):
    result = night.run_night(models(), gate)
    steps = result["first_response"]["steps"]
    assert [(s["step"], s["target"]) for s in steps] == [("suspend_account", "svc-maint-p04"),
        ("quarantine_workstation", "ws-fin-117"), ("close_remote_session", "jump-p04-01")]
    done = [e for e in gate.tools.executed if e["agent_id"] == FIRST and not e["tool"].endswith(".read")]
    assert [e["tool"] for e in done] == ["identity.account.suspend", "endpoint.quarantine", "remote_access.session.close"]
    assert "Account suspended | svc-maint-p04" in result["page"] and "Undone by" in result["page"]


def test_the_first_response_agent_is_refused_on_the_plant_floor_and_outside_the_incident(gate):
    tries = (ask("quarantine_workstation", device="ews-b2-01"), ask("close_remote_session", device="plc-b2-01"),
             ask("quarantine_workstation", device="ws-hr-044"), ask("suspend_account", account="employee-0412"),
             ask("suspend_account", account="svc-maint-p04"), ask("suspend_account", account="svc-maint-p04"))
    result = night.run_night(models(first=first_script(*tries)), gate)
    outcome = [a["failed"] for a in result["runs"][0]["steps"][1]["asked"]]
    assert outcome == [True, True, True, True, False, True]
    assert "on the plant floor" in result["runs"][0]["steps"][1]["asked"][0]["result"]
    assert len(result["first_response"]["steps"]) == 1
    assert not any(e["call"].get("target") == "ews-b2-01" for e in gate.tools.executed)


def test_nothing_on_the_plant_floor_is_carried_out_by_the_night(gate):
    result = night.run_night(models(), gate)
    assert [h["decision"] for h in result["held"]] == ["require_approval"] * 2
    assert not any(e["tool"] == "network.isolate" for e in gate.tools.executed)
    assert "held there" in result["page"]


def test_no_agent_holds_a_permission_it_does_not_need(gate):
    for agent in (FIRST, CHALLENGER):
        assert gate.execute(agent, "network.isolate", {"isolation_point": B2})["rule"] == "PERM-1"
    assert gate.execute(CHALLENGER, "identity.account.suspend", {"target": "x"})["rule"] == "PERM-1"
    assert gate.execute(PLANNER, "identity.account.suspend", {"target": "x"})["rule"] == "PERM-1"
    assert gate.execute(FIRST, "plc.write", {})["decision"] == "deny"


def test_an_agent_missing_from_the_registry_cannot_take_a_step(tmp_path):
    cards = {k: v for k, v in night.gateway().registry.items() if k != FIRST}
    bare = Gateway(registry=cards, audit=AuditLog(tmp_path / "a.jsonl"), killswitch=KillSwitch(tmp_path / "k.json"))
    result = night.run_night(models(), bare)
    assert result["first_response"]["steps"] == []
    assert all(a["failed"] and "REG-1" in a["result"] for a in asked(result, FIRST, "suspend_account"))


def test_the_kill_switch_on_the_first_response_agent_stops_its_steps_only(gate):
    gate.killswitch.kill(FIRST)
    result = night.run_night(models(), gate)
    assert result["first_response"]["steps"] == [] and result["plan"] is not None


def test_every_step_of_every_agent_is_in_the_control_tower_record(gate):
    result = night.run_night(models(), gate)
    records = gate.audit.records()
    for agent in (FIRST, PLANNER, CHALLENGER):
        calls = sum(len(s["asked"]) for r in result["runs"] if r["agent"] == agent for s in r["steps"])
        hand_ins = sum(1 for r in result["runs"] if r["agent"] == agent)
        filed = len(result["held"]) if agent == PLANNER else 0
        assert sum(1 for r in records if r["agent_id"] == agent) == calls - hand_ins + filed
    assert gate.audit.verify() == (True, "chain intact")


# -- what the harness accepts from the planner --------------------------------
def test_a_plan_with_a_figure_the_pricing_tool_did_not_produce_is_handed_back(gate):
    invented = plan([B2, LINK], [[B2, LINK], [PLANT]], why="It costs EUR 99,000, the least.")
    priced = plan([B2, LINK], [[B2, LINK], [PLANT]], why="It costs EUR 120,000, which is EUR 165,500 less than "
                  "disconnecting the whole plant floor at EUR 285,500. A stopped line-hour costs EUR 15,000.")
    result = night.run_night(models(planner=planner_script(invented, priced)), gate)
    tries = asked(result, PLANNER, "submit_plan")
    assert tries[0]["failed"] and "EUR 99,000" in tries[0]["result"] and not tries[1]["failed"]
    assert "EUR 99,000" not in result["page"] and "EUR 165,500 less" in result["page"]


def test_a_plan_with_an_unpriced_or_unknown_response_is_handed_back(gate):
    unpriced = plan([B2, LINK], [[B2, LINK], [LINK, PLANT]])
    unknown = plan([B2, "cut-everything"], [[B2, LINK], [PLANT]])
    alone = plan([B2, LINK], [[B2, LINK]])
    result = night.run_night(models(planner=planner_script(unpriced, unknown, alone, GOOD_PLAN)), gate)
    tries = asked(result, PLANNER, "submit_plan")
    assert [t["failed"] for t in tries] == [True, True, True, False]
    assert "has not been priced" in tries[0]["result"] and "Not a response step" in tries[1]["result"]
    assert "at least two" in tries[2]["result"]


def test_the_page_takes_its_figures_from_the_pricing_tool_not_from_the_agents(gate):
    result = night.run_night(models(), gate)
    by_name = {o["name"]: o for o in result["options"]}
    assert by_name["Disconnect the whole plant floor"]["cost_eur"] == 285500
    assert result["options"][0]["points"] == [B2, LINK] and result["options"][-1]["points"] == []
    assert "| 1 | Disconnect Line B, cell 2 and close the link between office side and plant floor **(recommended)** | EUR 120,000 |" in result["page"]


def test_a_planner_that_does_not_hand_in_leaves_a_page_that_says_so(gate):
    result = night.run_night(models(planner=[{"text": "", "stop": "refused"}]), gate)
    assert result["plan"] is None and result["held"] == [] and result["challenge"] is None
    assert "The planner agent did not hand in a plan." in result["page"]
    assert "decides without a recommendation" in result["page"] and "EUR 285,500" in result["page"]
    assert len(night.run_night(models(planner=[{"text": "", "stop": "refused"}]), gate)["options"]) == 4


# -- the debate ---------------------------------------------------------------
def test_when_the_challenger_agrees_the_planner_is_not_asked_again(gate):
    result = night.run_night(models(), gate)
    assert [r["agent"] for r in result["runs"]].count(PLANNER) == 1


def test_an_objection_goes_back_to_the_planner_which_keeps_its_plan_and_answers(gate):
    objection = challenge("object", "Line B, cell 2 alone is cheaper. Is closing the link needed?", alternative=[B2])
    answer = [turn(ask("price_response", steps=[B2])),
              turn(plan([B2, LINK], [[B2, LINK], [PLANT], [B2]], answer="Cell 2 alone leaves the remote access open."))]
    result = night.run_night(models(planner=planner_script(GOOD_PLAN) + answer, challenger=objection), gate)
    page = result["page"]
    assert [r["agent"] for r in result["runs"]] == [FIRST, PLANNER, CHALLENGER, PLANNER]
    assert "**The challenger objects.**" in page and "> Line B, cell 2 alone is cheaper." in page
    assert "The planner kept its recommendation and answers:" in page and "> Cell 2 alone leaves the remote access open." in page
    assert "It proposes response" in page and "Whether other cells are already touched." in page


def test_the_planner_sees_the_objection_and_may_change_its_recommendation(gate):
    objection = challenge("object", "The whole plant floor is the only response that does not depend on the map being right.",
                          alternative=[PLANT], price=([PLANT],))
    change = [turn(plan([PLANT], [[B2, LINK], [PLANT]], answer="Accepted: the map has been wrong before."))]
    used = models(planner=planner_script(GOOD_PLAN) + change, challenger=objection)
    result = night.run_night(used, gate)
    assert "does not depend on the map being right" in used[PLANNER].asked[-1]["turns"][0]["text"]
    assert result["recommended"] == [PLANT] and result["first_plan"]["recommended"] == f"{B2}+{LINK}"
    assert "The planner changed its recommendation and answers:" in result["page"]
    assert [h["isolation_point"] for h in result["held"]] == [PLANT]


def test_an_answer_without_an_answer_is_handed_back(gate):
    objection = challenge("object", "Cell 2 alone is cheaper.", alternative=[B2])
    silent = [turn(plan([B2, LINK], [[B2, LINK], [PLANT]])), turn(plan([B2, LINK], [[B2, LINK], [PLANT]], answer="It leaves the link open."))]
    result = night.run_night(models(planner=planner_script(GOOD_PLAN) + silent, challenger=objection), gate)
    tries = [a for a in result["runs"][3]["steps"] for a in a["asked"]]
    assert tries[0]["failed"] and "Answer the challenger" in tries[0]["result"] and not tries[1]["failed"]


def test_a_challenge_must_carry_an_argument_and_a_priced_alternative(gate):
    script = [turn(ask("submit_challenge", verdict="object", argument="", alternative=[LINK, PLANT])),
              turn(ask("submit_challenge", verdict="maybe", argument="Hm.")),
              turn(ask("submit_challenge", verdict="object", argument="It would save EUR 1,000,000.")),
              turn(ask("submit_challenge", verdict="agree", argument="Prices checked."))]
    result = night.run_night(models(challenger=script), gate)
    assert [t["failed"] for t in asked(result, CHALLENGER, "submit_challenge")] == [True, True, True, False]


def test_a_missing_challenge_is_stated_on_the_page(gate):
    result = night.run_night(models(challenger=[{"text": "", "stop": "limit"}]), gate)
    assert "The recommendation has not been challenged." in result["page"]


# -- a night on which no response closes every path ---------------------------
HARD = "no-safe-response"
HARD_PRICES = ([], [B2], [LINK], [B2, LINK])


def test_on_the_harder_night_the_plant_wide_disconnection_is_not_on_the_list(gate):
    script = planner_script(plan([PLANT], [[PLANT], [B2]]),
                            plan([B2, LINK], [[B2, LINK], [B2]], open_="Line C stays within reach."), price=HARD_PRICES)
    result = night.run_night(models(planner=script, challenger=challenge(price=())), gate, night=HARD)
    tries = asked(result, PLANNER, "submit_plan")
    assert tries[0]["failed"] and "Not a response step that is available tonight" in tries[0]["result"]
    assert "Not available tonight: Disconnect the whole plant floor." in result["page"]


def test_the_page_says_in_plain_words_that_no_response_closes_every_path(gate):
    script = planner_script(plan([B2, LINK], [[B2, LINK], [B2]], open_="Line C stays within reach until 07:00."),
                            price=HARD_PRICES)
    result = night.run_night(models(planner=script, challenger=challenge(price=())), gate, night=HARD)
    assert all(o["lines_still_reachable"] for o in result["options"])
    assert result["plan"]["closes_every_path"] is False
    assert "**No response available tonight closes every path.**" in result["page"]
    assert "It leaves Line C within the intruder's reach, with EUR 720,000 at stake" in result["page"]
    assert "> Line C stays within reach until 07:00." in result["page"]


def test_a_planner_that_hides_what_its_recommendation_leaves_open_is_handed_back(gate):
    script = planner_script(plan([B2, LINK], [[B2, LINK], [B2]]),
                            plan([B2, LINK], [[B2, LINK], [B2]], open_="Line C stays within reach."), price=HARD_PRICES)
    result = night.run_night(models(planner=script, challenger=challenge(price=())), gate, night=HARD)
    tries = asked(result, PLANNER, "submit_plan")
    assert tries[0]["failed"] and "leaves lines within the intruder's reach" in tries[0]["result"]


# -- the company briefing -----------------------------------------------------
def test_every_agent_reads_the_company_briefing(gate):
    briefing = load("briefing.json")
    briefing["what_matters_in_this_order"].insert(0, "Line A carries an order with a penalty clause tonight.")
    used = models()
    night.run_night(used, gate, briefing=briefing)
    for agent in (FIRST, PLANNER, CHALLENGER):
        system = used[agent].asked[0]["system"]
        assert "1. Line A carries an order with a penalty clause tonight." in system
        assert "Halden Industrial" in system and OWNER in system


def test_removing_a_step_from_the_briefing_takes_it_from_the_agent_without_changing_code(gate):
    briefing = load("briefing.json")
    del briefing["first_response"]["allowed_steps"]["quarantine_workstation"]
    briefing["first_response"]["never_suspend"] = ["svc-maint-p04"]
    result = night.run_night(models(), gate, briefing=briefing)
    assert [(s["step"], s["target"]) for s in result["first_response"]["steps"]] == [("close_remote_session", "jump-p04-01")]
    refused = [a["result"] for a in result["runs"][0]["steps"][1]["asked"] if a["failed"]]
    assert "never suspended without a person" in refused[0] and "does not allow the step" in refused[1]


def test_the_briefing_sets_how_many_responses_fit_on_the_page_and_how_often_the_challenger_speaks(gate):
    briefing = load("briefing.json")
    briefing["debate"] = {"challenge_rounds": 0, "options_on_the_page": 2}
    script = planner_script(GOOD_PLAN, plan([B2, LINK], [[B2, LINK], [PLANT]]))
    result = night.run_night(models(planner=script), gate, briefing=briefing)
    assert "At most 2 responses" in asked(result, PLANNER, "submit_plan")[0]["result"]
    assert [r["agent"] for r in result["runs"]] == [FIRST, PLANNER] and result["challenge"] is None


def test_a_briefing_that_names_another_decider_than_the_registry_stops_the_night(gate):
    briefing = load("briefing.json")
    briefing["who_decides"]["role"] = "Plant Manager"
    with pytest.raises(ValueError, match="They must agree"):
        night.run_night(models(), gate, briefing=briefing)


# -- the decision -------------------------------------------------------------
def test_only_the_named_person_can_choose_and_a_refused_attempt_is_recorded(gate):
    result = night.run_night(models(), gate)
    with pytest.raises(ApprovalError, match=OWNER):
        decision.decide(gate, result, 1, "Plant Manager")
    assert not any(e["tool"] == "network.isolate" for e in gate.tools.executed)
    last = gate.audit.records()[-1]
    assert (last["tool"], last["decision"], last["approved_by"]) == ("decision.choose", "rejected", "Plant Manager")


def test_choosing_the_recommended_response_releases_what_was_held(gate):
    result = night.run_night(models(), gate)
    outcome = decision.decide(gate, result, 1, OWNER)
    assert outcome["chosen"]["points"] == [B2, LINK]
    assert [(s["decision"], s["executed"]) for s in outcome["carried_out"]] == [("allow", True)] * 2
    isolated = [e["call"]["isolation_point"] for e in gate.tools.executed if e["tool"] == "network.isolate"]
    assert isolated == [B2, LINK]
    chosen = next(r for r in gate.audit.records() if r["tool"] == "decision.choose")
    assert chosen["decision"] == "chosen" and chosen["approved_by"] == OWNER
    assert chosen["params"] == {"incident": "no-case-memory/INC-001", "response": 1, "lost_output_eur": 120000, "recommended": True,
                                "challenger": "agree", "what": outcome["chosen"]["name"]}
    assert gate.audit.verify()[0]


def test_choosing_another_response_refuses_what_was_held_and_carries_out_the_choice(gate):
    objection = challenge("object", "The whole plant floor does not depend on the map.", alternative=[PLANT], price=([PLANT],))
    keep = [turn(plan([B2, LINK], [[B2, LINK], [PLANT], [B2]], answer="The map was checked in October."))]
    result = night.run_night(models(planner=planner_script(GOOD_PLAN) + keep, challenger=objection), gate)
    number = next(n for n, o in enumerate(result["options"], 1) if o["points"] == [PLANT])
    outcome = decision.decide(gate, result, number, OWNER)
    isolated = [e["call"]["isolation_point"] for e in gate.tools.executed if e["tool"] == "network.isolate"]
    assert isolated == [PLANT] and outcome["carried_out"][0]["executed"]
    records = gate.audit.records()
    assert sum(1 for r in records if r["tool"] == "approval.refuse") == 2
    chosen = next(r for r in records if r["tool"] == "decision.choose")
    assert chosen["params"]["recommended"] is False and chosen["params"]["challenger"] == "object"


def test_there_is_no_response_outside_the_page(gate):
    result = night.run_night(models(), gate)
    with pytest.raises(ApprovalError):
        decision.decide(gate, result, 9, OWNER)


def test_a_night_can_be_saved_and_decided_from_the_saved_copy(gate):
    result = json.loads(json.dumps(night.run_night(models(), gate)))
    assert decision.decide(gate, result, 1, OWNER)["carried_out"][0]["executed"]


def test_a_quiet_night_has_no_incident_and_asks_no_model(gate, monkeypatch):
    quiet = night.load_night()
    quiet["office"]["alerts"], quiet["floor"]["events"] = quiet["office"]["alerts"][:1], quiet["floor"]["events"][:2]
    monkeypatch.setattr(night, "load_night", lambda name: copy.deepcopy(quiet))
    used = models()
    result = night.run_night(used, gate)
    assert result["incident"] is None and all(m.asked == [] for m in used.values())
