"""The foundations of the service desk solution: data, suite stand-in, connector, ladder.

Fixed code only. No model is involved anywhere in this file, and no key is needed.
"""
import json
from collections import Counter
from datetime import datetime, timedelta

import pytest

from control_tower.audit import AuditLog
from control_tower.gateway import Gateway
from control_tower.killswitch import KillSwitch
from servicedesk import DATA, RESOLUTION, SUITE_AGENT, VERIFIER, Refused, generate, load
from servicedesk.connector import OPERATIONS, Connector
from servicedesk.ladder import BY_THE_LADDER, Ladder, NotAccepted
from servicedesk.suite import Suite, SuiteProblem

TICKETS = load("tickets.json")["tickets"]
KEY = load("answer-key.json")["tickets"]
TYPES = load("ticket-types.json")["types"]
BRIEFING = load("briefing.json")
DECIDER = "Head of IT Service Management"
CLOSED = [t for t in TICKETS if t["state"] == "closed"]
BY_ID = {t["id"]: t for t in TICKETS}


@pytest.fixture
def desk(tmp_path):
    """A gateway with its own audit trail, a fresh suite and a fresh ladder."""
    gateway = Gateway(audit=AuditLog(tmp_path / "audit.jsonl"), killswitch=KillSwitch(tmp_path / "kill.json"))
    ladder = Ladder(path=tmp_path / "ladder.jsonl", audit=gateway.audit)
    return Connector(gateway, Suite(), ladder)


def an_open(kind: str) -> str:
    return next(t["id"] for t in TICKETS if t["state"] == "open" and t["type"] == kind)


def clean(ladder: Ladder, kind: str, count: int, start: int = 0) -> None:
    for number in range(start, start + count):
        ladder.record_case(kind, f"T-{number}", "ok", "verified closure")


# -- the synthetic service desk ------------------------------------------------
def test_there_are_200_tickets_and_the_page_can_quote_their_make_up():
    assert len(TICKETS) == 200 and len(CLOSED) == 150
    assert Counter(t["closed_by"] for t in CLOSED) == {
        SUITE_AGENT: 64, "service desk staff": 76, "OT security team": 10}
    assert len({t["type"] for t in TICKETS}) == len(TYPES) == 10
    assert sum(t["state"] == "open" and TYPES[t["type"]]["route"] == "hand over" for t in TICKETS) == 6
    assert Counter(t["suite_group"] for t in TICKETS if t["suite_group"]) == {
        "VPN fails at plant 07": 10, "Printer driver at plant 03": 8}


def test_the_same_seed_writes_the_same_files():
    built = generate.build()
    for name, content in built.items():
        assert json.loads((DATA / name).read_text(encoding="utf-8")) == json.loads(json.dumps(content)), name


def test_people_appear_by_number_or_role_and_never_by_name():
    allowed = ("HI-EMP-", "not an employee", "unknown caller")
    assert all(t["requester"].startswith(allowed) for t in TICKETS)
    assert all(t.get("closed_by") in (None, SUITE_AGENT, "service desk staff", "OT security team") for t in TICKETS)


def test_the_planted_flaws_are_counted_and_none_is_marked_on_a_ticket():
    assert set(KEY) == {t["id"] for t in CLOSED}
    flaws = Counter((not k["fix_held"], not k["requester_entitled"], not k["record_matches"]) for k in KEY.values())
    assert flaws == {(False, False, False): 124, (True, False, False): 16,
                     (False, True, False): 5, (False, False, True): 5}
    by_suite_agent = sum(not all(KEY[t["id"]].values()) for t in CLOSED if t["closed_by"] == SUITE_AGENT)
    assert by_suite_agent == 16
    text = json.dumps(TICKETS)
    assert "fix_held" not in text and "requester_entitled" not in text and "record_matches" not in text


def test_every_planted_flaw_can_be_found_from_what_the_suite_shows_and_no_sound_ticket_looks_flawed():
    """The answer key is consistent with the evidence a check could read, in both directions."""
    suite = Suite()
    confirmations = BRIEFING["entitlement"]["confirmations_that_count"]
    for ticket in CLOSED:
        key, log = KEY[ticket["id"]], suite.log(ticket["id"])
        came_back = any(l["requester"] == ticket["requester"] and l["type"] == ticket["type"]
                        and l["about"] == ticket["about"] for l in suite.later(ticket["id"], BRIEFING["follow_up_days"]))
        assert came_back == (not key["fix_held"]), ticket["id"]
        done = [a["action"] for a in log["actions"] if a["actor"] == ticket["closed_by"]]
        assert (ticket["resolution"]["action"] in done) == key["record_matches"], ticket["id"]
        if ticket["type"] in ("password-reset", "mfa-reset", "recovery-contact-change"):
            entitled = (suite.owner(ticket["about"])["owner"] == ticket["requester"]
                        and ticket["identity_check"] in confirmations)
            assert entitled == key["requester_entitled"], ticket["id"]
        elif ticket["type"] == "access-request":
            approved = any(a["action"] == "approved the access request"
                           and a["actor"] == suite.owner(ticket["about"])["owner"] for a in log["actions"])
            assert approved == key["requester_entitled"], ticket["id"]
        else:
            assert key["requester_entitled"]


def test_a_note_that_says_a_test_was_made_is_backed_by_the_log_unless_the_mismatch_is_planted():
    """Found by the verifier in the first real runs: notes said 'Connection tested' and the log held no test."""
    suite, claims = Suite(), {"Connection tested": "connection test passed", "Test page printed": "test page printed",
                              "was informed": "requester informed"}
    checked = 0
    for ticket in CLOSED:
        for words, test in claims.items():
            if words in ticket["resolution"]["note"] and KEY[ticket["id"]]["record_matches"]:
                assert test in [a["action"] for a in suite.log(ticket["id"])["actions"]], ticket["id"]
                checked += 1
    assert checked == 38                    # every closed VPN and printer ticket


def test_a_follow_up_is_never_linked_to_the_ticket_it_follows():
    assert not any("follow" in key or "parent" in key for t in TICKETS for key in t)


def test_times_are_in_order_and_before_the_morning_of_the_data():
    as_of = load("tickets.json")["as_of"]
    for ticket in TICKETS:
        assert ticket["opened"] < as_of
        if ticket["state"] == "closed":
            assert ticket["opened"] < ticket["closed_at"] < as_of
    silent = [t for t in CLOSED if t["resolution"]["action"] == "closed after 72 hours without a reply"]
    assert len(silent) == 3
    assert all(datetime.fromisoformat(t["closed_at"]) - datetime.fromisoformat(t["opened"]) == timedelta(hours=72)
               for t in silent)


def test_the_briefing_the_types_and_the_ladder_agree_with_each_other():
    ladder = Ladder()
    on_ladder = {k for k, v in TYPES.items() if v["route"] == "ladder"}
    assert set(ladder.types()) == on_ladder
    assert all(v.get("hand_over_to") for v in TYPES.values() if v["route"] == "hand over")
    assert ladder.decider == BRIEFING["who_decides"]["role"] == DECIDER
    touching = {k for k, v in TYPES.items() if v["touches_identity"]}
    assert touching == set(BRIEFING["entitlement"]) - {"_note", "confirmations_that_count"}
    assert all(ladder.ceiling(k) != "act_alone" for k in touching)        # identity is never worked alone
    assert all(ladder.order.index(ladder.level(k)) <= ladder.order.index(ladder.ceiling(k)) for k in on_ladder)


def test_the_decider_is_the_accountable_owner_of_both_registry_cards():
    registry = Gateway().registry
    assert registry[RESOLUTION]["owner"] == registry[VERIFIER]["owner"] == DECIDER
    assert registry[VERIFIER]["autonomy"] == "advise"
    assert not any(tool.endswith((".update", ".delete")) for tool in registry[VERIFIER]["permissions"]["tools"])


# -- the suite stand-in ----------------------------------------------------------
def test_the_suite_keeps_the_note_and_the_action_log_apart():
    suite = Suite()
    mismatch = next(i for i, k in KEY.items() if not k["record_matches"] and BY_ID[i]["type"] == "access-request")
    assert suite.get(mismatch)["resolution"]["action"] == "grant read access"
    assert "grant write access" in [a["action"] for a in suite.log(mismatch)["actions"]]


def test_the_suite_offers_only_its_own_fixes_and_changes_only_open_tickets():
    suite = Suite()
    with pytest.raises(SuiteProblem, match="not a fix the suite offers"):
        suite.resolve(an_open("vpn-connection"), "anyone", "format the laptop", "Done.")
    with pytest.raises(SuiteProblem, match="only an open ticket"):
        suite.resolve(CLOSED[0]["id"], "anyone", "reinstall the VPN profile", "Again.")
    with pytest.raises(SuiteProblem, match="no ticket"):
        suite.get("SD-26-9999")


# -- the connector ---------------------------------------------------------------
def test_the_connector_offers_ten_operations_and_none_serves_the_answer_key(desk):
    assert len(desk.operations()) == len(OPERATIONS) == 10
    assert not any("key" in name or "answer" in name or "reopen" in name or "delete" in name for name in OPERATIONS)
    closed = CLOSED[0]["id"]
    seen = json.dumps([desk.call(VERIFIER, op, ticket=closed) for op in
                       ("get_ticket", "get_owner", "get_action_log", "get_later_tickets")]
                      + [desk.call(VERIFIER, "search_tickets", state="closed", limit=200)])
    assert "fix_held" not in seen and "requester_entitled" not in seen and "record_matches" not in seen
    assert not hasattr(desk.suite, "key")


def test_every_call_is_recorded_by_the_control_tower_under_the_agents_own_identity(desk):
    desk.call(VERIFIER, "get_ticket", ticket=CLOSED[0]["id"])
    desk.call(RESOLUTION, "search_tickets", state="open", type="printer")
    records = desk.gateway.audit.records()
    assert [(r["agent_id"], r["tool"], r["decision"]) for r in records] == [
        (VERIFIER, "ticket.read", "allow"), (RESOLUTION, "ticket.read", "allow")]
    assert records[0]["params"]["operation"] == "get_ticket"
    assert desk.gateway.audit.verify()[0]


def test_the_verifier_cannot_close_or_change_a_ticket_whatever_the_ladder_says(desk):
    assert desk.ladder.permits("vpn-connection", "act_with_check") and desk.ladder.level("mfa-reset") == "watch"
    for kind in ("vpn-connection", "mfa-reset", "plant-terminal"):      # the highest rung in use, the lowest, and a hand-over type
        ticket, fix = an_open(kind), (TYPES[kind]["actions"] or ["restart it"])[0]
        for operation, given in (("resolve", {"action": fix, "note": "Done."}),
                                 ("add_note", {"text": "Looks solved."}),
                                 ("propose_fix", {"action": fix, "note": "Try this."}),
                                 ("confirm_requester", {}),
                                 ("hand_over", {"why": "Not mine."})):
            with pytest.raises(Refused) as refused:
                desk.call(VERIFIER, operation, ticket=ticket, **given)
            assert refused.value.verdict["rule"] == "PERM-1"
        assert desk.suite.ticket(ticket)["state"] == "open"
    assert not desk.suite.notes
    assert len([r for r in desk.gateway.audit.records() if r["decision"] == "deny"]) == 15   # each refusal is on record


def test_an_identity_that_is_not_in_the_registry_gets_nothing(desk):
    with pytest.raises(Refused) as refused:
        desk.call("sd-triage", "get_ticket", ticket=CLOSED[0]["id"])
    assert refused.value.verdict["rule"] == "REG-1"


def test_the_resolution_agent_closes_a_ticket_on_a_type_that_has_earned_it(desk):
    ticket = an_open("vpn-connection")
    closed = desk.call(RESOLUTION, "resolve", ticket=ticket, action="reinstall the VPN profile",
                       note="VPN profile reinstalled.")
    assert closed["state"] == "closed" and closed["closed_by"] == RESOLUTION
    assert desk.suite.log(ticket)["actions"][-1] == {
        "at": desk.suite.as_of, "actor": RESOLUTION, "action": "reinstall the VPN profile",
        "target": closed["about"]["id"]}
    last = desk.gateway.audit.records()[-1]
    assert (last["agent_id"], last["tool"], last["decision"]) == (RESOLUTION, "ticket.update", "allow")


def test_the_ladder_refuses_what_a_type_has_not_earned_and_the_refusal_is_recorded(desk):
    ticket = an_open("mfa-reset")                            # a type on 'watch'
    with pytest.raises(Refused, match="approved by the Head of IT Service Management, never by an agent") as refused:
        desk.call(RESOLUTION, "resolve", ticket=ticket,
                  action="reset the second factor and enrol the owner's registered phone", note="Done.")
    assert refused.value.verdict["rule"] == "LADDER"
    with pytest.raises(Refused):
        desk.call(RESOLUTION, "propose_fix", ticket=ticket,
                  action="reset the second factor and enrol the owner's registered phone", note="Try this.")
    assert desk.suite.ticket(ticket)["state"] == "open"
    denied = [r for r in desk.gateway.audit.records() if r["rule"] == "LADDER"]
    assert len(denied) == 2 and all(r["decision"] == "deny" and r["source"] == "autonomy-ladder" for r in denied)
    assert not any(r["decision"] == "allow" for r in desk.gateway.audit.records())   # nothing was let through first


def test_on_watch_the_agents_note_is_kept_but_not_shown_on_the_ticket(desk):
    watched, proposing = an_open("mfa-reset"), an_open("printer")
    desk.call(RESOLUTION, "add_note", ticket=watched, text="I would reset the second factor.")
    desk.call(RESOLUTION, "propose_fix", ticket=proposing, action="roll back the printer driver",
              note="The fault began with the update.")
    assert desk.suite.notes[watched][0]["kind"] == "shadow" and desk.suite.get(watched)["notes"] == []
    assert desk.suite.get(proposing)["notes"][0]["kind"] == "proposal"
    with pytest.raises(Refused):                             # 'propose' is not 'act'
        desk.call(RESOLUTION, "resolve", ticket=proposing, action="roll back the printer driver", note="Done.")


def test_plant_floor_and_security_tickets_can_only_be_handed_over_and_go_where_the_company_says(desk):
    for kind in ("plant-terminal", "security-report"):
        ticket = an_open(kind)
        with pytest.raises(Refused) as refused:
            desk.call(RESOLUTION, "add_note", ticket=ticket, text="Restart the terminal.")
        assert refused.value.verdict["rule"] == "HANDOVER"
        handed = desk.call(RESOLUTION, "hand_over", ticket=ticket, why="Plant floor.", to="myself")
        assert handed["state"] == "handed over"
        assert handed["handed_to"] == "OT/IT Convergence Sentinel (solution 02)"
    assert desk.call(RESOLUTION, "hand_over", ticket=an_open("printer"), why="Needs a technician on site.")[
        "handed_to"] == "service desk staff"


def test_the_kill_switch_stops_the_resolution_agent_at_the_connector(desk):
    desk.gateway.killswitch.kill(RESOLUTION)
    with pytest.raises(Refused) as refused:
        desk.call(RESOLUTION, "get_ticket", ticket=CLOSED[0]["id"])
    assert refused.value.verdict["rule"] == "KILL"
    assert desk.call(VERIFIER, "get_ticket", ticket=CLOSED[0]["id"])["id"] == CLOSED[0]["id"]


def test_a_request_the_suite_cannot_carry_out_is_a_problem_not_a_crash(desk):
    with pytest.raises(SuiteProblem, match="offers no operation"):
        desk.call(RESOLUTION, "reopen", ticket=CLOSED[0]["id"])
    with pytest.raises(SuiteProblem, match="not a fix the suite offers"):
        desk.call(RESOLUTION, "resolve", ticket=an_open("vpn-connection"), action="format the laptop", note="Done.")
    with pytest.raises(SuiteProblem, match="not closed"):
        desk.call(VERIFIER, "get_later_tickets", ticket=an_open("printer"))


# -- the autonomy ladder ---------------------------------------------------------
def test_a_step_up_needs_enough_clean_cases_and_then_the_one_role_that_may_approve(tmp_path):
    ladder = Ladder(path=tmp_path / "ladder.jsonl")
    clean(ladder, "printer", 19)
    assert not ladder.standing("printer")["ready_for_step_up"]
    with pytest.raises(NotAccepted, match="not ready"):
        ladder.approve("printer", DECIDER)
    clean(ladder, "printer", 1, start=19)
    assert ladder.standing("printer")["next"] == "act_with_check" and ladder.level("printer") == "propose"
    for nobody in (RESOLUTION, VERIFIER, "Chief Information Officer", BY_THE_LADDER):
        with pytest.raises(NotAccepted, match="Only the Head of IT Service Management"):
            ladder.approve("printer", nobody)
    move = ladder.approve("printer", DECIDER)
    assert (move["from"], move["to"], move["by"], len(move["evidence"])) == ("propose", "act_with_check", DECIDER, 20)
    assert ladder.level("printer") == "act_with_check"
    assert ladder.standing("printer")["checked_since_last_move"] == 0      # one rung at a time: the count starts again


def test_too_many_failed_cases_block_a_step_up(tmp_path):
    ladder = Ladder(path=tmp_path / "ladder.jsonl")
    clean(ladder, "printer", 18)
    for number in (1, 2):
        ladder.record_case("printer", f"F-{number}", "failed", "verified closure")
    standing = ladder.standing("printer")
    assert not standing["ready_for_step_up"] and standing["failed_share"] == 0.1
    assert ladder.level("printer") == "propose"                           # 10% blocks a step up and causes no step down


def test_a_serious_finding_steps_a_type_down_at_once_without_anyone_approving(tmp_path):
    audit = AuditLog(tmp_path / "audit.jsonl")
    ladder = Ladder(path=tmp_path / "ladder.jsonl", audit=audit)
    clean(ladder, "password-reset", 12)
    outcome = ladder.record_case("password-reset", "SD-26-0146", "serious", "verified closure", closed_by=SUITE_AGENT,
                                 finding="The requester was not the owner of the account.")
    move = outcome["move"]
    assert (move["from"], move["to"], move["direction"], move["by"]) == ("act_with_check", "propose", "down", BY_THE_LADDER)
    assert move["evidence"] == ["SD-26-0146"] and ladder.level("password-reset") == "propose"
    record = audit.records()[-1]
    assert (record["tool"], record["rule"], record["approved_by"]) == ("ladder.step_down", "LADDER", None)


def test_a_step_down_takes_effect_at_the_connector_on_the_next_call(desk):
    first, second = [t["id"] for t in TICKETS if t["state"] == "open" and t["type"] == "password-reset"
                     and t["identity_check"] == "signed-in session"][:2]
    action = TYPES["password-reset"]["actions"][0]
    desk.call(RESOLUTION, "resolve", ticket=first, action=action, note="Password reset.")
    desk.ladder.record_case("password-reset", first, "serious", "verified closure", closed_by=RESOLUTION,
                            finding="The requester was not the owner of the account.")
    with pytest.raises(Refused) as refused:
        desk.call(RESOLUTION, "resolve", ticket=second, action=action, note="Password reset.")
    assert refused.value.verdict["rule"] == "LADDER" and desk.suite.ticket(second)["state"] == "open"


def test_a_failed_share_above_the_limit_steps_a_type_down_one_rung(tmp_path):
    ladder = Ladder(path=tmp_path / "ladder.jsonl")
    clean(ladder, "vpn-connection", 8)
    assert ladder.record_case("vpn-connection", "F-1", "failed", "verified closure")["move"] is None   # 1 of 9: too few cases
    assert ladder.record_case("vpn-connection", "F-2", "failed", "verified closure")["move"]["to"] == "propose"  # 2 of 10
    assert ladder.moves("vpn-connection")[0]["evidence"] == ["F-1", "F-2"]


def test_a_type_on_the_lowest_rung_cannot_fall_further(tmp_path):
    ladder = Ladder(path=tmp_path / "ladder.jsonl")
    outcome = ladder.record_case("mfa-reset", "SD-1", "serious", "note compared with what the person did")
    assert outcome["move"] is None and ladder.level("mfa-reset") == "watch"


def test_a_step_down_can_be_reversed_by_the_same_role_with_a_reason_and_all_of_it_is_on_record(tmp_path):
    ladder = Ladder(path=tmp_path / "ladder.jsonl")
    down = ladder.record_case("mailbox-full", "SD-9", "serious", "verified closure",
                              finding="The note says the archive was enabled; the log shows nothing.")["move"]
    with pytest.raises(NotAccepted, match="Only the Head of IT Service Management"):
        ladder.restore("mailbox-full", RESOLUTION, "Please.")
    with pytest.raises(NotAccepted, match="needs a reason"):
        ladder.restore("mailbox-full", DECIDER, " ")
    back = ladder.restore("mailbox-full", DECIDER, "The log entry was delayed by the suite; the archive was enabled.")
    assert (back["to"], back["direction"], back["reverses"]) == ("act_with_check", "restored", down["seq"])
    assert ladder.level("mailbox-full") == "act_with_check"
    assert [e["kind"] for e in ladder.events()] == ["case", "move", "move"]
    with pytest.raises(NotAccepted, match="nothing to reverse"):
        ladder.restore("mailbox-full", DECIDER, "Again.")


def test_no_evidence_lifts_a_type_above_its_ceiling(tmp_path):
    ladder = Ladder(path=tmp_path / "ladder.jsonl")
    clean(ladder, "password-reset", 40)
    assert not ladder.standing("password-reset")["ready_for_step_up"]
    with pytest.raises(NotAccepted, match="ceiling"):
        ladder.approve("password-reset", DECIDER)
    clean(ladder, "recovery-contact-change", 20)
    ladder.approve("recovery-contact-change", DECIDER)                     # watch -> propose: its ceiling
    clean(ladder, "recovery-contact-change", 20, start=20)
    with pytest.raises(NotAccepted, match="ceiling"):
        ladder.approve("recovery-contact-change", DECIDER)


def test_the_ladder_accepts_only_its_own_types_and_outcomes(tmp_path):
    ladder = Ladder(path=tmp_path / "ladder.jsonl")
    with pytest.raises(NotAccepted, match="not on the ladder"):
        ladder.record_case("plant-terminal", "SD-1", "ok", "verified closure")
    with pytest.raises(NotAccepted, match="not an outcome"):
        ladder.record_case("printer", "SD-1", "fine", "verified closure")
    assert ladder.events() == []


def test_changing_the_ladder_file_changes_what_an_agent_may_do_without_code(tmp_path):
    config = load("ladder.json")
    config["start"]["mfa-reset"] = "act_with_check"
    gateway = Gateway(audit=AuditLog(tmp_path / "audit.jsonl"), killswitch=KillSwitch(tmp_path / "kill.json"))
    desk = Connector(gateway, Suite(), Ladder(config=config, path=tmp_path / "ladder.jsonl"))
    signed_in = next(t["id"] for t in TICKETS if t["state"] == "open" and t["type"] == "mfa-reset"
                     and t["identity_check"] == "signed-in session")
    closed = desk.call(RESOLUTION, "resolve", ticket=signed_in,
                       action=TYPES["mfa-reset"]["actions"][0], note="Second factor reset.")
    assert closed["state"] == "closed"
