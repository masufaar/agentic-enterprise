"""The two agents on prepared replies: the scenarios run every time, without a key.

A scripted stand-in replays fixed replies in place of a model. It is not a model and
proves nothing about one; it exercises the fixed code around the agents.
"""
import pytest

from control_tower.audit import AuditLog
from control_tower.gateway import Gateway
from harness.model import Scripted
from warroom import load
from warroom.prepared import REPLIES
from warroom.session import Session, run_scenario


def run(name, tmp_path):
    return run_scenario(Scripted(list(REPLIES[name])), name, folder=tmp_path / name)


# -- the single-source halt ----------------------------------------------------
def test_halt_maps_the_exposure(tmp_path):
    r = run("single-source-halt", tmp_path)
    note = r["exposures"]["EV-01"]
    assert note["material"] and note["kind"] == "stoppage"
    assert note["revenue_at_risk_eur"] == 1143000 and note["min_days_of_cover"] == 12
    assert set(note["affected_products"]) == {"PRD-A", "PRD-B", "PRD-C", "PRD-F"}

def test_halt_holds_two_drafts_for_sign_off(tmp_path):
    r = run("single-source-halt", tmp_path)
    assert len(r["held"]) == 2
    assert all(d["held_for"] == "Head of Supply Chain" for d in r["held"])
    kinds = {d["kind"] for d in r["held"]}
    assert kinds == {"purchase_order", "email"}

def test_halt_records_a_sound_case_on_the_ladder(tmp_path):
    r = run("single-source-halt", tmp_path)
    row = next(x for x in r["ladder"] if x["type"] == "new_po_qualified")
    assert row["cases_since_last_move"] == 1 and row["failed"] == 0

def test_halt_agrees_with_the_answer_key(tmp_path):
    r = run("single-source-halt", tmp_path)
    assert r["score"] == {"events_compared": 1, "agreed": 1, "differences": []}

def test_halt_hands_back_one_bad_filing(tmp_path):
    r = run("single-source-halt", tmp_path)
    assert len(r["handed_back"]) == 1

def test_halt_audit_chain_intact(tmp_path):
    r = run("single-source-halt", tmp_path)
    assert r["audit"]["chain"] == "chain intact"


# -- the tariff (a cost, not a stoppage) ---------------------------------------
def test_tariff_is_a_cost_exposure(tmp_path):
    r = run("tariff-cost", tmp_path)
    note = r["exposures"]["EV-02"]
    assert note["material"] and note["kind"] == "cost"
    assert note["revenue_at_risk_eur"] == 1116000
    assert set(note["affected_products"]) == {"PRD-A", "PRD-C", "PRD-D", "PRD-F"}

def test_tariff_holds_a_qualified_po(tmp_path):
    r = run("tariff-cost", tmp_path)
    assert len(r["held"]) == 1 and r["held"][0]["action_type"] == "new_po_qualified"
    assert r["score"]["agreed"] == 1


# -- the false alarm -----------------------------------------------------------
def test_rumour_is_not_material(tmp_path):
    r = run("false-alarm", tmp_path)
    assert r["exposures"]["EV-05"]["material"] is False

def test_rumour_draws_no_response_and_no_draft(tmp_path):
    r = run("false-alarm", tmp_path)
    assert r["held"] == []
    respond = [s for s in r["steps"] if s["step"] == "respond"][0]
    assert respond.get("skipped")

def test_rumour_agrees_with_the_answer_key(tmp_path):
    r = run("false-alarm", tmp_path)
    assert r["score"]["agreed"] == 1


# -- every scenario writes a page ----------------------------------------------
@pytest.mark.parametrize("name", list(REPLIES))
def test_scenario_writes_a_page(name, tmp_path):
    r = run(name, tmp_path)
    assert r["page"].startswith("# Supply chain disruption")
    assert "Head of Supply Chain" in r["page"]


# -- the agent property: a case changes the next one ---------------------------
def test_a_case_is_offered_to_the_next_event(tmp_path):
    """Two events about the same supplier: the second run can read the first as a case."""
    session = Session(tmp_path / "mem", Gateway(audit=AuditLog(tmp_path / "a.jsonl")))
    first = REPLIES["single-source-halt"][: len(REPLIES["single-source-halt"])]  # monitor + sourcing of EV-01
    # assess EV-01 with the monitor replies only (first 5), then check memory holds a case
    monitor_replies = first[:5]
    session_model = Scripted(list(monitor_replies))
    session.assess(session_model, "EV-01")
    assert session.cases and session.cases[0]["about_id"] == "SUP-NORD"
    # the connector would now offer that case to a monitor reading SUP-NORD again
    session.connector.cases = session.cases
    offered = session.connector.call("disruption-monitor", "read_cases", about="SUP-NORD")
    assert offered["earlier_cases"] and offered["earlier_cases"][0]["event"] == "EV-01"
