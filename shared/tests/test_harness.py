"""The shared harness on its own: the hook to the Control Tower, the loop, the checks, the case book.

The hook tests run against the real gateway of solution 01 with its real registry
and rules, in a temporary folder, so nothing here depends on solution 02.
"""
import pytest
from control_tower.audit import AuditLog
from control_tower.gateway import Gateway
from control_tower.killswitch import KillSwitch

from harness import Refused, act, tool_call_request
from harness.cases import CaseBook
from harness.checks import foreign_amounts, too_long
from harness.loop import Tool, ToolProblem, run_agent
from harness.model import Scripted
from harness.page import quote

PLANNER = "ot-response"  # an approved agent of solution 02, used here only as a registered identity


@pytest.fixture
def gateway(tmp_path):
    return Gateway(audit=AuditLog(tmp_path / "audit.jsonl"), killswitch=KillSwitch(tmp_path / "kill.json"))


def announce(gateway, tool, call, agent=PLANNER, **more):
    return tool_call_request(gateway, {"agent_id": agent, "tool": tool, "input": call, **more})


# -- the hook: allow, deny, ask ------------------------------------------------
def test_an_allowed_call_comes_back_as_allow_and_is_carried_out(gateway):
    answer = announce(gateway, "incident.read", {"incident": "INC-1"})
    assert answer["decision"] == "allow" and answer["executed"] is True
    assert answer["verdict"]["decision"] == "allow" and answer["audit_seq"] == answer["verdict"]["audit_seq"]


def test_a_refused_call_comes_back_as_deny(gateway):
    answer = announce(gateway, "erp.payment.release", {"amount_eur": 10})
    assert answer["decision"] == "deny" and answer["rule"] == "PERM-1" and answer["executed"] is False


def test_an_agent_not_in_the_registry_is_denied(gateway):
    assert announce(gateway, "incident.read", {}, agent="nobody")["rule"] == "REG-1"


def test_a_stopped_agent_is_denied(gateway):
    gateway.killswitch.kill(PLANNER)
    answer = announce(gateway, "incident.read", {"incident": "INC-1"})
    assert answer["decision"] == "deny" and answer["rule"] == "KILL"


def test_a_held_call_comes_back_as_ask_and_nothing_is_carried_out(gateway):
    answer = announce(gateway, "network.isolate", {"isolation_point": "x", "what": "x", "plant": "plant-04"})
    assert answer["decision"] == "ask" and answer["executed"] is False
    assert answer["verdict"]["decision"] == "require_approval"


def test_the_held_call_is_allowed_when_the_accountable_person_makes_it(gateway):
    owner = gateway.registry[PLANNER]["owner"]
    call = {"isolation_point": "x", "what": "x", "plant": "plant-04"}
    assert announce(gateway, "network.isolate", call, approved_by=owner, source="approver")["decision"] == "allow"
    assert announce(gateway, "network.isolate", call, approved_by="Somebody else")["decision"] == "ask"


def test_the_volume_limit_comes_back_as_deny(gateway):
    limit = gateway.policies["volume_limit"]
    tool, cap = limit["tools"][0], limit["rows_per_agent_per_day"]
    agent = next(a for a, card in gateway.registry.items() if tool in card["permissions"]["tools"]
                 and card["approval"].get("status") == "approved")
    data_class = gateway.registry[agent]["permissions"]["data_classes"][0]
    first = announce(gateway, tool, {"rows": cap, "data_class": data_class}, agent=agent)
    assert first["decision"] == "allow", first
    over = announce(gateway, tool, {"rows": 1, "data_class": data_class}, agent=agent)
    assert over["decision"] == "deny" and over["rule"] == "V-002"
    unstated = announce(gateway, tool, {"data_class": data_class}, agent=agent)
    assert unstated["decision"] == "deny" and unstated["rule"] == "V-001"


def test_an_answer_the_harness_does_not_know_is_treated_as_deny():
    class Odd:
        def execute(self, agent_id, tool, call):
            return {"decision": "maybe", "rule": None, "reason": "unclear"}
    assert tool_call_request(Odd(), {"agent_id": "a", "tool": "t"})["decision"] == "deny"


def test_every_announcement_is_in_the_record(gateway):
    announce(gateway, "incident.read", {"incident": "INC-1"})
    announce(gateway, "erp.payment.release", {})
    assert [r["decision"] for r in gateway.audit.records()] == ["allow", "deny"]


def test_act_raises_for_deny_and_for_ask_and_keeps_the_gateways_verdict(gateway):
    assert act(gateway, PLANNER, "incident.read", {"incident": "INC-1"})["decision"] == "allow"
    with pytest.raises(Refused) as denied:
        act(gateway, PLANNER, "erp.payment.release", {})
    assert denied.value.answer == "deny" and denied.value.verdict["rule"] == "PERM-1"
    with pytest.raises(Refused) as held:
        act(gateway, PLANNER, "network.isolate", {"isolation_point": "x", "what": "x", "plant": "plant-04"})
    assert held.value.answer == "ask"


# -- the loop -----------------------------------------------------------------
def call(name, **given):
    return {"tool_calls": [{"id": name, "name": name, "input": given}]}


def test_a_denied_tool_is_told_to_the_agent_which_carries_on_to_its_hand_in(gateway):
    def pay(_):
        return act(gateway, PLANNER, "erp.payment.release", {})

    def hand_in(given):
        if "refused" not in given["text"]:
            raise ToolProblem("Not accepted. Say what was refused.")
        return given
    tools = [Tool("pay", "Release a payment.", pay),
             Tool("hand_in", "Hand in.", hand_in, {"text": {"type": "string"}}, hand_in=True)]
    model = Scripted([call("pay"), call("hand_in", text="done"), call("hand_in", text="payment refused")])
    run = run_agent("tester", model, "system", "task", tools)
    assert run["ended"] == "handed in" and run["result"] == {"text": "payment refused"}
    asked = [a for step in run["steps"] for a in step["asked"]]
    assert [a["failed"] for a in asked] == [True, True, False] and "PERM-1" in asked[0]["result"]


def test_an_agent_that_never_hands_in_runs_out_of_turns():
    model = Scripted([{"text": "thinking"}] * 3)
    run = run_agent("tester", model, "s", "t", [Tool("hand_in", "Hand in.", lambda g: g, hand_in=True)], max_turns=3)
    assert run["ended"] == "out of turns" and run["result"] is None


# -- hand-in checks, case book, page ------------------------------------------
def test_word_limits_and_figures():
    assert too_long({"why": 3}, why="one two three") == []
    assert "limit is 3" in too_long({"why": 3}, why="one two three four", other="not limited at all")[0]
    known = {120000, 287250}
    assert foreign_amounts(known, "It costs EUR 120,000, or EUR 287.250.") == []
    assert foreign_amounts(known, "About EUR 125,000 and EUR 1.5 million") == ["EUR 125,000", "EUR 1.5"]


def test_the_case_book_writes_through_the_control_tower(gateway, tmp_path):
    class Book(CaseBook):
        writer = "ot-briefing"
    book = Book(tmp_path / "cases")
    assert book.next_id() == "CASE-001"
    book.write(gateway, {"case": "CASE-001", "status": "waiting for decision"})
    assert book.next_id() == "CASE-002" and book.get("CASE-001")["status"] == "waiting for decision"
    assert gateway.audit.records()[-1]["tool"] == "cases.write"
    with pytest.raises(Refused):  # the default writer is not in the registry: nothing is written
        CaseBook(tmp_path / "other").write(gateway, {"case": "CASE-001", "status": "x"})
    assert not (tmp_path / "other").exists()


def test_an_agents_words_are_shown_as_a_quotation():
    assert quote("one\n\ntwo") == ["> one", "> two"] and quote("") == ["> (nothing written)"]
