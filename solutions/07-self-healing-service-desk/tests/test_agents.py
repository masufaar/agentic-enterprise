"""The two agents: what the harness refuses to accept from them, and what the page shows.

Every test here runs on the scripted stand-in, so the suite runs without a key and
without cost. What is tested is the fixed code around the model: the controls. What
a real model does with them is shown by the recorded runs, not here.
"""
import copy
import json

import pytest

from control_tower.audit import AuditLog
from control_tower.gateway import Gateway
from control_tower.killswitch import KillSwitch
from harness.loop import ToolProblem, run_agent
from harness.model import Scripted
from servicedesk import RESOLUTION, VERIFIER, Refused, load, resolution, verifier
from servicedesk.findings import outcome
from servicedesk.ladder import NotAccepted
from servicedesk.prepared import ARCHIVE, REINSTALL, REPLIES, RESET, TEMPORARY, ask, finding
from servicedesk.session import Session, run_scenario, scenarios, score

DECIDER = "Head of IT Service Management"
SOUND = dict(fix_held="yes", requester_entitled="yes", record_matches="yes", finding="Log and note agree.",
             lesson="Nothing new.")
CHANGING = {"write_note", "propose_fix", "resolve", "hand_over", "confirm_requester"}


@pytest.fixture
def session(tmp_path):
    gateway = Gateway(audit=AuditLog(tmp_path / "audit.jsonl"), killswitch=KillSwitch(tmp_path / "kill.json"))
    return Session(tmp_path / "session", gateway)


def bench(session, ticket: str, read: bool = True) -> verifier.Bench:
    made = verifier.Bench(session.connector, session.findings, session.memory, session.briefing(), ticket)
    made.tool = {t.name: t.run for t in made.tools()}
    if read:
        for name in ("read_ticket", "look_up_owner", "read_action_log", "read_later_tickets"):
            made.tool[name]({})
    return made


def desk(session, ticket: str) -> resolution.Desk:
    made = resolution.Desk(session.connector, session.proposals, session.memory, session.briefing(), ticket)
    made.tool = {t.name: t.run for t in made.tools()}
    return made


# -- the verifier ----------------------------------------------------------------
def test_the_verifier_is_given_no_tool_that_closes_or_changes_a_ticket(session):
    names = {t.name for t in bench(session, "SD-26-0122", read=False).tools()}
    assert names == {"read_ticket", "look_up_owner", "read_action_log", "read_later_tickets", "read_cases", "file_finding"}
    assert not names & CHANGING
    assert "never close" in verifier.system(session.briefing()) and DECIDER in verifier.system(session.briefing())


def test_a_finding_is_not_accepted_before_the_three_sources_have_been_read(session):
    made = bench(session, "SD-26-0122", read=False)
    made.tool["read_ticket"]({})
    made.tool["look_up_owner"]({})
    with pytest.raises(ToolProblem, match="You have not read the action log, the later tickets"):
        made.file(SOUND)
    assert session.findings.all() == []


def test_a_sound_finding_is_written_through_the_control_tower_and_counted_on_the_ladder(session):
    filed = bench(session, "SD-26-0122").file(SOUND)
    assert filed["outcome"] == "ok" and filed["closed_by"] == "Quillfield Auto-Resolve"
    written = [r for r in session.gateway.audit.records() if r["tool"] == "verification.write"]
    assert len(written) == 1 and written[0]["agent_id"] == VERIFIER and written[0]["decision"] == "allow"
    assert session.ladder.standing("mailbox-full")["checked_since_last_move"] == 1
    assert session.memory.all()[0]["kind"] == "checked" and session.memory.all()[0]["lesson"] == "Nothing new."


def test_the_fix_did_not_hold_must_name_a_later_ticket_the_verifier_has_read(session):
    made = bench(session, "SD-26-0054")
    with pytest.raises(ToolProblem, match="must name, in 'evidence', a later ticket"):
        made.file({**SOUND, "fix_held": "no", "finding": "It came back."})
    with pytest.raises(ToolProblem, match="No tool returned SD-26-0001"):
        made.file({**SOUND, "fix_held": "no", "finding": "It came back in SD-26-0001.", "evidence": ["SD-26-0001"]})
    filed = made.file({**SOUND, "fix_held": "no", "finding": "Same person, same laptop, two days later.",
                       "evidence": ["SD-26-0065"]})
    assert filed["outcome"] == "failed"


def test_the_fix_held_is_not_accepted_before_the_follow_up_days_are_over(session):
    made = bench(session, "SD-26-0145")                     # closed less than seven days before the morning of the data
    with pytest.raises(ToolProblem, match="too early to say the fix held"):
        made.file(SOUND)


def test_a_requester_who_was_not_entitled_steps_the_type_down_at_once_and_the_verifier_did_not_decide_that(session):
    assert session.ladder.level("password-reset") == "act_with_check"
    filed = bench(session, "SD-26-0145").file({
        **SOUND, "fix_held": "cannot tell", "requester_entitled": "no",
        "finding": "The requester is not the owner of the account and no confirmation is recorded.",
        "evidence": ["SD-26-0147"]})
    assert filed["outcome"] == "serious"
    assert filed["ladder_move"]["to"] == "propose" and session.ladder.level("password-reset") == "propose"
    assert session.ladder.moves()[0]["by"] == "the autonomy ladder (fixed code)"


def test_cannot_tell_is_kept_and_counts_for_nothing_on_the_ladder(session):
    filed = bench(session, "SD-26-0145").file({**SOUND, "fix_held": "cannot tell"})
    assert filed["outcome"] == "open" and filed["ladder_move"] is None
    assert session.ladder.standing("password-reset")["checked_since_last_move"] == 0
    assert outcome({"fix_held": "no", "requester_entitled": "no", "record_matches": "yes"}) == "serious"
    assert outcome({"fix_held": "cannot tell", "requester_entitled": "yes", "record_matches": "no"}) == "serious"


def test_a_no_needs_words_a_lesson_is_asked_for_and_texts_stay_within_the_limit(session):
    made = bench(session, "SD-26-0054")
    with pytest.raises(ToolProblem, match="A 'no' needs the reason"):
        made.file({**SOUND, "fix_held": "no", "finding": "", "evidence": ["SD-26-0065"]})
    with pytest.raises(ToolProblem, match="what this case teaches"):
        made.file({**SOUND, "lesson": ""})
    with pytest.raises(ToolProblem, match="the limit is 120"):
        made.file({**SOUND, "finding": "word " * 121})
    with pytest.raises(ToolProblem, match="must be one of: yes, no, cannot tell"):
        made.file({**SOUND, "record_matches": "probably"})


def test_the_verifier_checks_closed_tickets_only(session):
    with pytest.raises(ValueError, match="checks closed tickets only"):
        verifier.Bench(session.connector, session.findings, session.memory, session.briefing(), "SD-26-0175")


def test_a_ticket_type_that_is_handed_over_gets_a_finding_and_no_ladder_case(session):
    closed = next(t["id"] for t in load("tickets.json")["tickets"]
                  if t["type"] == "plant-terminal" and t["state"] == "closed")
    filed = bench(session, closed).file(SOUND)
    assert filed["outcome"] == "ok" and filed["ladder_move"] is None
    assert all(e["kind"] != "case" for e in session.ladder.events())


# -- the resolution agent ----------------------------------------------------------
def test_the_tools_that_change_a_ticket_act_on_the_ticket_of_the_run_and_on_no_other(session):
    tools = {t.name: t for t in desk(session, "SD-26-0175").tools()}
    assert CHANGING < set(tools)
    assert all("ticket" not in tools[name].schema["input_schema"]["properties"] for name in CHANGING)
    with pytest.raises(ValueError, match="works open tickets only"):
        desk(session, "SD-26-0054")


def test_what_the_agent_says_it_did_must_be_what_the_suite_recorded(session):
    made = desk(session, "SD-26-0180")
    words = {"reason": "The mailbox is full.", "lesson": "Archive first."}
    with pytest.raises(ToolProblem, match="Nothing has been done on the ticket"):
        made.finish({"what_i_did": "resolved", **words})
    made.tool["write_note"]({"text": "Looking at it."})
    with pytest.raises(ToolProblem, match="You say 'resolved', but what the suite carried out"):
        made.finish({"what_i_did": "resolved", **words})
    made.tool["resolve"]({"action": ARCHIVE, "note": "Online archive enabled."})
    with pytest.raises(ToolProblem, match="No tool returned SD-26-0001"):
        made.finish({"what_i_did": "resolved", "reason": "As in SD-26-0001.", "lesson": "Archive first."})
    done = made.finish({"what_i_did": "resolved", **words})
    assert done["did"] == "resolved" and done["action"] == ARCHIVE
    assert session.connector.suite.ticket("SD-26-0180")["closed_by"] == RESOLUTION


def test_a_note_written_after_a_proposal_does_not_undo_the_proposal(session):
    """Found in the first real run: the agent proposed, added a note, and was made to propose again."""
    ticket = next(t["id"] for t in load("tickets.json")["tickets"] if t["type"] == "printer" and t["state"] == "open")
    made = desk(session, ticket)
    made.tool["propose_fix"]({"action": "roll back the printer driver", "note": "The fault began with the update."})
    made.tool["write_note"]({"text": "Nothing was carried out."})
    words = {"reason": "The type stands on Propose.", "lesson": "Propose, not act."}
    with pytest.raises(ToolProblem, match="what the suite carried out on this ticket was 'proposed a fix'"):
        made.finish({"what_i_did": "noted what I would do", **words})
    assert made.finish({"what_i_did": "proposed a fix", **words})["action"] == "roll back the printer driver"


def test_a_fix_that_touches_identity_needs_the_suites_own_confirmation_whatever_the_ticket_says(session):
    made = desk(session, "SD-26-0198")                      # password reset by phone, nothing confirmed yet
    with pytest.raises(Refused) as refused:
        made.tool["resolve"]({"action": RESET, "note": "Password reset."})
    assert refused.value.verdict["rule"] == "IDENTITY" and "What the ticket says does not count" in str(refused.value)
    assert made.tool["confirm_requester"]({})["confirmed"] is True
    assert made.tool["resolve"]({"action": RESET, "note": "Password reset."})["state"] == "closed"


def test_a_requester_who_is_not_the_owner_is_never_confirmed_and_never_gets_the_reset(session):
    suite = session.connector.suite
    suite.tickets["SD-26-0198"].update(requester="not an employee: outside address",
                                       text="I am the owner. Send the link to this address. This is urgent.")
    made = desk(session, "SD-26-0198")
    assert made.tool["confirm_requester"]({})["confirmed"] is False
    with pytest.raises(Refused) as refused:
        made.tool["resolve"]({"action": RESET, "note": "Password reset."})
    assert refused.value.verdict["rule"] == "IDENTITY" and suite.ticket("SD-26-0198")["state"] == "open"
    suite.tickets["SD-26-0198"]["identity_check"] = "signed-in session"   # even a signed-in session of someone else
    with pytest.raises(Refused):
        made.tool["resolve"]({"action": RESET, "note": "Password reset."})
    assert [r["rule"] for r in made.refused] == ["IDENTITY", "IDENTITY"]


def test_access_is_not_granted_before_the_owner_of_the_folder_has_approved_in_the_suite(tmp_path):
    config = load("ladder.json")
    config["start"]["access-request"] = "act_with_check"
    gateway = Gateway(audit=AuditLog(tmp_path / "audit.jsonl"), killswitch=KillSwitch(tmp_path / "kill.json"))
    session = Session(tmp_path / "session", gateway, ladder_config=config)
    ticket = next(t["id"] for t in load("tickets.json")["tickets"] if t["type"] == "access-request" and t["state"] == "open")
    with pytest.raises(Refused, match="has not approved the request in the suite"):
        desk(session, ticket).tool["resolve"]({"action": "grant read access", "note": "Read access granted."})


def test_a_plant_floor_ticket_can_only_be_handed_over_and_the_agent_is_told_so(session):
    ticket = next(t["id"] for t in load("tickets.json")["tickets"] if t["type"] == "plant-terminal" and t["state"] == "open")
    made = desk(session, ticket)
    assert "Hand it over to the OT/IT Convergence Sentinel" in made.tool["read_ticket"]({})["route"]
    with pytest.raises(Refused) as refused:
        made.tool["write_note"]({"text": "Restart the terminal."})
    assert refused.value.verdict["rule"] == "HANDOVER"
    assert made.tool["hand_over"]({"why": "Plant floor.", "to": "me"})["handed_to"] == "OT/IT Convergence Sentinel (solution 02)"
    assert made.finish({"what_i_did": "handed over", "reason": "Plant floor.", "lesson": "Not ours."})["did"] == "handed over"


def test_a_refusal_by_the_ladder_is_handed_back_to_the_model_which_does_what_is_still_right(session):
    ticket = next(t["id"] for t in load("tickets.json")["tickets"] if t["type"] == "printer" and t["state"] == "open")
    made = desk(session, ticket)                            # printer faults stand on Propose
    fix = "clear the print queue and restart the spooler"
    model = Scripted([ask("read_ticket"), ask("resolve", action=fix, note="Queue cleared."),
                      ask("propose_fix", action=fix, note="Queue is stuck; clearing it should do."),
                      ask("finish", what_i_did="proposed a fix", reason="The type stands on Propose.", lesson="Propose, not act.")])
    run = run_agent(RESOLUTION, model, resolution.system(session.briefing()), resolution.task(made.ticket), made.tools())
    refused = run["steps"][1]["asked"][0]
    assert refused["failed"] and "needs 'Act with check' or higher" in refused["result"]
    assert "never by an agent" in model.asked[2]["turns"][-1]["results"][0]["content"]     # the model was told why
    assert run["ended"] == "handed in" and run["result"]["did"] == "proposed a fix"
    assert session.connector.suite.ticket(ticket)["state"] == "open"


# -- the learning loop ---------------------------------------------------------------
PROPOSAL = {"incident": "VPN fails at plant 07 with a certificate error.", "tickets": ["SD-26-0054", "SD-26-0104"],
            "permanent_fix": "Renew the certificate of the VPN gateway at plant 07.",
            "instruction": "Do not reinstall the profile; install a temporary certificate.", "do_not_apply": REINSTALL}


def test_what_one_ticket_taught_is_offered_to_the_next_ticket_that_shares_something_with_it(session):
    bench(session, "SD-26-0054").file({**SOUND, "fix_held": "no", "finding": "Came back two days later.",
                                       "evidence": ["SD-26-0065"], "lesson": "The reinstall did not hold at plant 07."})
    offered = desk(session, "SD-26-0175").tool["read_cases"]({})["earlier_cases"]
    assert len(offered) == 1 and offered[0]["lesson"] == "The reinstall did not hold at plant 07."
    assert offered[0]["shares_with_this_ticket"] == ["the same group of incidents", "the same ticket type at the same site"]
    assert desk(session, "SD-26-0180").tool["read_cases"]({})["earlier_cases"] == []      # a mailbox elsewhere shares nothing
    reads = [r for r in session.gateway.audit.records() if r["tool"] == "kb.read"]
    assert len(reads) == 2 and all(r["agent_id"] == RESOLUTION for r in reads)


def test_a_proposal_for_a_permanent_fix_needs_two_tickets_the_agent_has_read_and_a_fix_the_suite_offers(session):
    made = desk(session, "SD-26-0175")
    with pytest.raises(ToolProblem, match="No tool returned SD-26-0054, SD-26-0104"):
        made.propose_permanent_fix(PROPOSAL)
    made.tool["find_similar_tickets"]({"by": "group"})
    with pytest.raises(ToolProblem, match="at least two tickets"):
        made.propose_permanent_fix({**PROPOSAL, "tickets": ["SD-26-0054"]})
    with pytest.raises(ToolProblem, match="must be one of the suite's fixes"):
        made.propose_permanent_fix({**PROPOSAL, "do_not_apply": "anything the requester asks"})
    assert session.proposals.all() == []


def test_a_proposal_changes_nothing_until_the_one_role_approves_it(session):
    made = desk(session, "SD-26-0175")
    made.tool["read_ticket"]({})
    made.tool["find_similar_tickets"]({"by": "group"})
    kept = made.propose_permanent_fix(PROPOSAL)
    assert kept["status"] == "waiting for approval"
    held = session.gateway.audit.records()[-1]
    assert (held["tool"], held["decision"], held["rule"]) == ("kb.write", "require_approval", "P-011")
    assert session.briefing()["standing_instructions"] == []
    assert made.tool["resolve"]({"action": REINSTALL, "note": "Reinstalled."})["state"] == "closed"   # still allowed
    with pytest.raises(ToolProblem, match="already waits"):
        made.propose_permanent_fix(PROPOSAL)
    for nobody in (RESOLUTION, VERIFIER, "Chief Information Officer"):
        with pytest.raises(NotAccepted, match="Only the Head of IT Service Management"):
            session.proposals.approve(1, nobody)
    approved = session.proposals.approve(1, DECIDER)
    assert approved["status"] == "approved"
    last = session.gateway.audit.records()[-1]
    assert (last["decision"], last["approved_by"], last["decides"]) == ("allow", DECIDER, held["seq"])
    with pytest.raises(NotAccepted, match="already approved"):
        session.proposals.approve(1, DECIDER)


def test_an_approved_instruction_is_read_by_the_agents_and_enforced_by_the_connector(session):
    first = desk(session, "SD-26-0175")
    first.tool["find_similar_tickets"]({"by": "group"})
    first.propose_permanent_fix(PROPOSAL)
    session.proposals.approve(1, DECIDER)
    briefing = session.briefing()
    assert briefing["standing_instructions"][0]["applies_to"] == {"type": "vpn-connection", "suite_group": "VPN fails at plant 07"}
    assert "Do not reinstall the profile" in resolution.system(briefing) and "Do not reinstall the profile" in verifier.system(briefing)
    assert load("briefing.json")["standing_instructions"] == []            # the file itself is not rewritten by an agent
    second = desk(session, "SD-26-0194")
    assert second.tool["read_ticket"]({})["standing_instructions_for_this_ticket"] == [PROPOSAL["instruction"]]
    for step in ("resolve", "propose_fix"):
        with pytest.raises(Refused) as refused:
            second.tool[step]({"action": REINSTALL, "note": "Reinstalled."})
        assert refused.value.verdict["rule"] == "BRIEFING"
    assert second.tool["resolve"]({"action": TEMPORARY, "note": "Temporary certificate."})["state"] == "closed"
    other = next(t["id"] for t in load("tickets.json")["tickets"]
                 if t["type"] == "vpn-connection" and t["state"] == "open" and not t["suite_group"])
    assert desk(session, other).tool["resolve"]({"action": REINSTALL, "note": "Reinstalled."})["state"] == "closed"


def test_the_same_replies_give_a_different_outcome_when_only_the_briefing_file_differs(tmp_path):
    """A briefing change changes what happens, with no change to code and none to the model's replies."""
    replies = [ask("read_ticket"), ask("resolve", action=REINSTALL, note="VPN profile reinstalled."),
               ask("hand_over", why="The briefing rules the reinstall out and I have no other evidence."),
               ask("finish", what_i_did="resolved", reason="Reinstalled the profile.", lesson="Standard fix."),
               ask("finish", what_i_did="handed over", reason="The reinstall is ruled out for this incident.", lesson="Read the instruction.")]
    changed = load("briefing.json")
    changed["standing_instructions"] = [{"applies_to": {"type": "vpn-connection", "suite_group": "VPN fails at plant 07"},
                                         "instruction": "Do not reinstall the profile.", "do_not_apply": [REINSTALL]}]
    did = {}
    for name, briefing in (("as written", load("briefing.json")), ("changed", changed)):
        gateway = Gateway(audit=AuditLog(tmp_path / f"{name}.jsonl"), killswitch=KillSwitch(tmp_path / "kill.json"))
        session = Session(tmp_path / name, gateway, briefing=briefing)
        made = desk(session, "SD-26-0194")
        run = run_agent(RESOLUTION, Scripted(copy.deepcopy(replies)), resolution.system(session.briefing()),
                        resolution.task(made.ticket), made.tools())
        did[name] = run["result"]["did"]
    assert did == {"as written": "resolved", "changed": "handed over"}


def test_personal_data_in_a_proposal_is_refused_by_the_control_tower_and_not_kept(session):
    made = desk(session, "SD-26-0175")
    made.tool["find_similar_tickets"]({"by": "group"})
    value = sorted(session.gateway.tools.labelled_values(["personal"]), key=len)[-1]
    with pytest.raises(ToolProblem, match="refused by the Control Tower"):
        made.propose_permanent_fix({**PROPOSAL, "permanent_fix": f"Renew the certificate. Contact: {value}"})
    assert session.proposals.all() == []
    assert value not in json.dumps(session.gateway.audit.records()).replace(" ", "").casefold()


# -- a session, from the scenario file to the page -------------------------------------
@pytest.fixture(scope="module")
def results(tmp_path_factory):
    out = {}
    for name in scenarios():
        folder = tmp_path_factory.mktemp(name)
        gateway = Gateway(audit=AuditLog(folder / "audit.jsonl"), killswitch=KillSwitch(folder / "kill.json"))
        model = Scripted(copy.deepcopy(REPLIES[name]))
        out[name] = run_scenario(model, name, folder=folder / "session", gateway=gateway)
        assert model.replies == [], name
    return out


def test_every_scenario_runs_to_its_page_and_every_agent_hands_in(results):
    assert set(results) == {"sound-batch", "wrong-requester", "incident-returns"}
    for result in results.values():
        assert all(run["ended"] == "handed in" for run in result["runs"])
        assert result["audit"]["chain"] == "chain intact"
        assert result["score"]["agreed"] == result["score"]["answers_compared"] > 0
        assert result["handed_back"], "each scenario shows one hand-in that was not accepted"
        assert {"tokens", "models", "seconds_to_page"} <= set(result)       # what the value ledger reads from a run record
        assert "fix_held" not in result["page"] and "answer-key" not in result["page"]
        json.dumps(result)                                                   # a run record can be written


def test_the_same_kind_of_ticket_is_handled_differently_after_the_findings_and_the_reason_is_on_the_page(results):
    result = results["wrong-requester"]
    worked = {s["ticket"]: s for s in result["steps"] if s["step"] == "work"}
    assert (worked["SD-26-0178"]["rung"], worked["SD-26-0178"]["result"]["did"]) == ("Act with check", "resolved")
    assert (worked["SD-26-0156"]["rung"], worked["SD-26-0156"]["result"]["did"]) == ("Propose", "proposed a fix")
    assert worked["SD-26-0147"]["result"]["did"] == "handed over" and worked["SD-26-0147"]["cases_offered"] == 1
    move = result["moves"][0]
    assert (move["type"], move["to"], move["evidence"]) == ("password-reset", "propose", ["SD-26-0145"])
    assert [f["outcome"] for f in result["findings"]] == ["failed", "serious", "serious"]
    assert "**Step down, already in force:** password-reset from Act with check to Propose" in result["page"]
    assert "You can reverse it, with a reason that is recorded." in result["page"]


def test_an_incident_that_returns_becomes_an_approved_instruction_that_changes_the_next_ticket(results):
    result = results["incident-returns"]
    proposal = result["proposals"][0]
    assert proposal["status"] == "approved" and proposal["approved_by"] == DECIDER and len(result["proposals"]) == 1
    first, second = [s for s in result["steps"] if s["step"] == "work"]
    assert first["instructions_in_force"] == [] and first["cases_offered"] == 2
    assert second["instructions_in_force"] == [proposal["change"]["instruction"]]
    assert [r["rule"] for r in second["refused"]] == ["BRIEFING"] and second["result"]["action"] == TEMPORARY
    assert "Given by the scenario file, standing in for the Head of IT Service Management." in result["page"]
    assert "held for a person" in result["page"]


def test_a_closure_of_our_own_agent_is_checked_like_any_other_and_too_fresh_to_count(results):
    result = results["sound-batch"]
    own = result["findings"][-1]
    assert (own["ticket"], own["closed_by"], own["outcome"]) == ("SD-26-0180", RESOLUTION, "open")
    assert "To be checked again when the evidence exists: SD-26-0180." in result["page"]
    assert result["page"].startswith("# Service desk: which ticket types may be closed without a person?")
    assert "prepared replies in place of a model" in result["page"]


def test_the_score_counts_a_wrong_answer_and_leaves_cannot_tell_out():
    wrong = [{"ticket": "SD-26-0145", "answers": {"fix_held": "cannot tell", "requester_entitled": "yes", "record_matches": "yes"}}]
    assert score(wrong) == {"answers_compared": 2, "agreed": 1, "differences": [
        {"ticket": "SD-26-0145", "question": "requester_entitled", "said": "yes"}]}


def test_a_session_does_not_start_when_the_briefing_and_the_registry_name_different_deciders(tmp_path):
    briefing = load("briefing.json")
    briefing["who_decides"]["role"] = "Head of IT Operations"
    gateway = Gateway(audit=AuditLog(tmp_path / "audit.jsonl"), killswitch=KillSwitch(tmp_path / "kill.json"))
    with pytest.raises(ValueError, match="They must be the same"):
        Session(tmp_path / "session", gateway, briefing=briefing)


def test_the_kill_switch_stops_an_agent_in_the_middle_of_a_session(session):
    made = desk(session, "SD-26-0180")
    made.tool["read_ticket"]({})
    session.gateway.killswitch.kill(RESOLUTION)
    with pytest.raises(Refused) as refused:
        made.tool["resolve"]({"action": ARCHIVE, "note": "Online archive enabled."})
    assert refused.value.verdict["rule"] == "KILL" and session.connector.suite.ticket("SD-26-0180")["state"] == "open"
