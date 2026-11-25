"""The foundations of the war room: data, the system stand-ins, the BOM walk, the connector, the ladder.

Fixed code only. No model is involved anywhere in this file, and no key is needed.
"""
import pytest

from control_tower.audit import AuditLog
from control_tower.gateway import Gateway
from control_tower.killswitch import KillSwitch
from warroom import MONITOR, SOURCING, Refused, load
from warroom.connector import Connector
from warroom.ladder import BY_THE_LADDER, Ladder, NotAccepted
from warroom.systems import ERP, Feed, SystemProblem

PARTS = load("parts.json")
SUPPLIERS = load("suppliers.json")["suppliers"]
ORDERS = load("orders.json")
EVENTS = load("events.json")["events"]
KEY = load("answer-key.json")["events"]


@pytest.fixture
def war(tmp_path):
    gateway = Gateway(audit=AuditLog(tmp_path / "audit.jsonl"), killswitch=KillSwitch(tmp_path / "kill.json"))
    ladder = Ladder(path=tmp_path / "ladder.jsonl", audit=gateway.audit)
    return Connector(gateway, ERP(), Feed(), ladder)


# -- data integrity ------------------------------------------------------------
def test_every_bom_part_exists():
    for prod in PARTS["products"].values():
        for line in prod["bom"]:
            assert line["part"] in PARTS["parts"], line

def test_every_primary_supplier_exists():
    for part in PARTS["parts"].values():
        assert part["primary_supplier"] in SUPPLIERS

def test_exactly_one_single_source_part():
    single = [pid for pid, p in PARTS["parts"].items() if p["single_source"]]
    assert single == ["PCM-7"]

def test_revenue_is_qty_times_price():
    for o in ORDERS["customer_orders"]:
        assert o["revenue_eur"] == o["qty"] * o["unit_price_eur"]

def test_answer_key_covers_every_event():
    assert {e["id"] for e in EVENTS} == set(KEY)

def test_the_unverified_event_is_a_rumour():
    rumours = [e["id"] for e in EVENTS if not e["verified"]]
    assert rumours == ["EV-05"]
    assert KEY["EV-05"]["material"] is False


# -- the BOM walk --------------------------------------------------------------
def test_trace_single_source_supplier_cascades(war):
    exp = war.call(MONITOR, "trace_exposure", kind="supplier", id="SUP-NORD")
    assert [p["id"] for p in exp["affected_parts"]] == ["PCM-7"]
    assert {p["id"] for p in exp["affected_products"]} == {"PRD-A", "PRD-B", "PRD-C", "PRD-F"}
    assert exp["revenue_at_risk_eur"] == 1143000
    assert exp["min_days_of_cover"] == 12

def test_trace_matches_the_answer_key_products(war):
    for event_id, truth in KEY.items():
        if not truth["material"] or truth["kind"] == "watch":
            continue
        event = next(e for e in EVENTS if e["id"] == event_id)
        exp = war.call(MONITOR, "trace_exposure", kind=event["about"]["kind"], id=event["about"]["id"])
        assert {p["id"] for p in exp["affected_products"]} == set(truth["hits_products"]), event_id

def test_trace_of_a_non_supplier_is_empty(war):
    exp = war.call(MONITOR, "trace_exposure", kind="supplier", id="SUP-OTHER")
    assert exp["affected_products"] == [] and exp["revenue_at_risk_eur"] == 0

def test_trace_revenue_only_counts_open_orders(war):
    exp = war.call(MONITOR, "trace_exposure", kind="part", id="PCM-7")
    assert exp["revenue_at_risk_eur"] == sum(
        o["revenue_eur"] for o in ORDERS["customer_orders"]
        if o["product"] in {p["id"] for p in exp["affected_products"]})


# -- the monitor reads only ----------------------------------------------------
def test_monitor_cannot_draft_a_po(war):
    with pytest.raises(Refused) as e:
        war.call(MONITOR, "draft_po", part="PCM-7", supplier="SUP-TORNA", qty=1, amount_eur=100, reason="x")
    assert e.value.verdict["rule"] == "PERM-1"

def test_monitor_cannot_send_email(war):
    with pytest.raises(Refused):
        war.call(MONITOR, "draft_supplier_email", to="x@y.example", subject="s", body="b")


# -- the sign-off gate ---------------------------------------------------------
def test_qualified_po_under_limit_is_held(war):
    d = war.call(SOURCING, "draft_po", part="PCM-7", supplier="SUP-TORNA", qty=400, amount_eur=21000, reason="bridge")
    assert d["held_for"] == "Head of Supply Chain"
    assert d["action_type"] == "new_po_qualified"

def test_unqualified_po_is_refused_by_the_ladder(war):
    with pytest.raises(Refused) as e:
        war.call(SOURCING, "draft_po", part="PCM-7", supplier="SUP-GREY", qty=400, amount_eur=8000, reason="cheap")
    assert e.value.verdict["rule"] == "UNQUALIFIED"

def test_po_over_the_spend_limit_is_denied(war):
    with pytest.raises(Refused) as e:
        war.call(SOURCING, "draft_po", part="PCM-7", supplier="SUP-TORNA", qty=2000, amount_eur=40000, reason="big")
    assert e.value.verdict["rule"] == "P-003"

def test_supplier_email_outside_domain_is_held(war):
    d = war.call(SOURCING, "draft_supplier_email", to="orders@tornelis.example", subject="s", body="b")
    assert d["held_for"] == "Head of Supply Chain"

def test_action_type_qualified_vs_unqualified(war):
    assert war.action_type("draft_po", {"part": "PCM-7", "supplier": "SUP-TORNA"}) == "new_po_qualified"
    assert war.action_type("draft_po", {"part": "PCM-7", "supplier": "SUP-GREY"}) == "new_po_unqualified"

def test_audit_chain_intact_after_calls(war):
    war.call(MONITOR, "trace_exposure", kind="supplier", id="SUP-NORD")
    war.call(SOURCING, "draft_po", part="PCM-7", supplier="SUP-TORNA", qty=1, amount_eur=100, reason="x")
    assert war.gateway.audit.verify()[0] is True


# -- the ladder ----------------------------------------------------------------
def test_unqualified_locked_at_watch(tmp_path):
    lad = Ladder(path=tmp_path / "l.jsonl")
    assert lad.level("new_po_unqualified") == "watch"
    assert lad.ceiling("new_po_unqualified") == "watch"

def _raise(lad: Ladder, kind: str) -> None:
    """Earn a type up one rung, the way the ladder allows: five sound cases, then the decider approves."""
    for i in range(5):
        lad.record_case(kind, f"OK-{i}", "ok", "sound")
    lad.approve(kind, "Head of Supply Chain")

def test_a_serious_case_steps_down_at_once(tmp_path):
    lad = Ladder(path=tmp_path / "l.jsonl")
    _raise(lad, "new_po_qualified")
    assert lad.level("new_po_qualified") == "act_with_check"
    out = lad.record_case("new_po_qualified", "EV-X", "serious", "bad", finding="acted on a rumour")
    assert out["move"]["direction"] == "down"
    assert lad.level("new_po_qualified") == "propose"

def test_step_up_needs_the_decider_and_evidence(tmp_path):
    lad = Ladder(path=tmp_path / "l.jsonl")
    for i in range(5):
        lad.record_case("new_po_qualified", f"EV-{i}", "ok", "sound")
    with pytest.raises(NotAccepted):
        lad.approve("new_po_qualified", "Someone Else")
    move = lad.approve("new_po_qualified", "Head of Supply Chain")
    assert move["direction"] == "up" and lad.level("new_po_qualified") == "act_with_check"

def test_step_down_is_recorded_as_by_the_ladder(tmp_path):
    lad = Ladder(path=tmp_path / "l.jsonl")
    _raise(lad, "expedite")
    lad.record_case("expedite", "EV-Y", "serious", "bad")
    down = [m for m in lad.moves("expedite") if m["direction"] == "down"][0]
    assert down["by"] == BY_THE_LADDER

def test_a_restore_reverses_a_step_down(tmp_path):
    lad = Ladder(path=tmp_path / "l.jsonl")
    _raise(lad, "expedite")
    lad.record_case("expedite", "EV-Z", "serious", "bad")
    assert lad.level("expedite") == "propose"
    lad.restore("expedite", "Head of Supply Chain", "the finding was wrong")
    assert lad.level("expedite") == "act_with_check"

def test_unknown_action_type_is_rejected(tmp_path):
    lad = Ladder(path=tmp_path / "l.jsonl")
    with pytest.raises(NotAccepted):
        lad.record_case("not_a_type", "EV-Q", "ok", "x")


# -- the connector offers nothing else -----------------------------------------
def test_unknown_operation_is_refused(war):
    with pytest.raises(SystemProblem):
        war.call(SOURCING, "delete_order", order="CO-001")

def test_systems_carry_invented_names():
    assert ERP().name == "Fenmark MRP"
    assert Feed().name == "Larkspur Supply Signals"
