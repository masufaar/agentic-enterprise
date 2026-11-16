"""Tests. Run from this solution folder with:  python -m pytest -q"""
import copy

import pytest

from sentinel import REPORTS, Refused, load
from sentinel import briefing, collection, correlation, response, workflow
from control_tower.approvals import ApprovalError, Approvals
from control_tower.audit import AuditLog
from control_tower.gateway import Gateway
from control_tower.killswitch import KillSwitch

AGENTS = ["ot-asset-discovery", "ot-threat-correlation", "ot-response", "ot-briefing"]
INCIDENT = ["IT-1", "IT-2", "IT-3", "IT-4", "OT-1", "OT-2", "OT-3", "OT-4"]
NOISE = ["IT-N1", "IT-N2", "OT-N1", "OT-N2", "OT-N3"]


@pytest.fixture
def gateway(tmp_path):
    return Gateway(audit=AuditLog(tmp_path / "audit.jsonl"), killswitch=KillSwitch(tmp_path / "kill.json"))


@pytest.fixture
def result(gateway):
    return workflow.run(gateway, write=False)


def option(result, *points):
    return next(o for o in result["assessments"][0]["options"] if o["points"] == list(points))


# -- registration ------------------------------------------------------------
def test_all_four_agents_are_registered_approved_and_owned(gateway):
    for agent in AGENTS:
        card = gateway.registry[agent]
        assert card["solution"] == "02-ot-it-convergence-sentinel"
        assert card["approval"]["status"] == "approved" and card["owner"]


def test_an_unregistered_agent_cannot_take_a_step(gateway):
    with pytest.raises(Refused) as refused:
        from sentinel import act
        act(gateway, "ot-shadow-agent", "network.read", {})
    assert refused.value.verdict["rule"] == "REG-1"


# -- agent 1: collection -----------------------------------------------------
def test_collection_puts_both_tools_into_one_format(gateway):
    alerts = collection.collect(gateway)["alerts"]
    assert len(alerts) == 13 and {a["side"] for a in alerts} == {"office", "plant"}
    keys = {"id", "time", "tool", "side", "origin", "target", "account", "kind", "severity", "text"}
    assert all(set(a) == keys and 1 <= a["severity"] <= 4 for a in alerts)
    assert [a["time"] for a in alerts] == sorted(a["time"] for a in alerts)


def test_kill_switch_on_the_collector_stops_the_whole_workflow(gateway):
    gateway.killswitch.kill("ot-asset-discovery")
    with pytest.raises(Refused) as refused:
        workflow.run(gateway, write=False)
    assert refused.value.verdict["rule"] == "KILL"


# -- agent 2: correlation ----------------------------------------------------
def test_correlation_finds_one_incident_and_sets_the_noise_aside(result):
    assert len(result["incidents"]) == 1
    assert result["incidents"][0]["alerts"] == INCIDENT
    assert sorted(u["id"] for u in result["unrelated"]) == NOISE


def test_incident_reaches_from_office_to_plant_floor(result):
    incident = result["incidents"][0]
    assert incident["sides"] == ["office", "plant"]
    assert incident["footholds"] == ["ws-fin-117", "jump-p04-01", "ews-b2-01"]
    assert incident["foothold_zones"] == ["office", "dmz", "cell-b2"]
    assert incident["lines_touched"] == ["line-b", "line-c"]
    assert incident["accounts_moved"] == ["svc-maint-p04"]


def test_an_alert_far_away_in_time_is_not_joined(gateway):
    collected = collection.collect(gateway)
    late = dict(collected["alerts"][-1], id="OT-LATE", time="2026-11-10T09:00:00Z")
    collected["alerts"].append(late)
    found = correlation.correlate(gateway, collected)
    assert found["incidents"][0]["alerts"] == INCIDENT
    assert "OT-LATE" in [u["id"] for u in found["unrelated"]]


def test_a_new_alert_on_a_device_of_the_incident_is_joined(gateway):
    collected = collection.collect(gateway)
    collected["alerts"].append({"id": "OT-NEW", "time": "2026-11-10T03:10:00Z", "tool": "x", "side": "plant",
                                "origin": "ews-b2-01", "target": "plc-b1-01", "account": None,
                                "kind": "controller_program_read", "severity": 4, "text": "x"})
    assert "OT-NEW" in correlation.correlate(gateway, collected)["incidents"][0]["alerts"]


def test_two_low_alerts_on_one_office_device_are_not_an_incident(gateway):
    collected = collection.collect(gateway)
    collected["alerts"] = [a for a in collected["alerts"] if a["id"] == "IT-N1"] * 2
    assert correlation.correlate(gateway, collected)["incidents"] == []


# -- agent 3: impact and response --------------------------------------------
def test_each_response_is_priced_in_lost_output(result):
    assert option(result)["cost_eur"] == 0
    assert option(result, "cut-cell-b2")["cost_eur"] == 120_000            # Line B, 8 h
    assert option(result, "cut-link-dmz-ot")["cost_eur"] == 0              # 4 h closed, 6 h of orders loaded
    assert option(result, "cut-plant-ot")["cost_eur"] == 465_500           # A 8 h + 12 h restart, B 8 h, C 3 h 02 min
    assert option(result, "cut-cell-b2", "cut-link-dmz-ot")["cost_eur"] == 120_000
    assert len(result["assessments"][0]["options"]) == 5


def test_whole_plant_price_adds_up_line_by_line(result):
    lines = {l["line"]: l for l in option(result, "cut-plant-ot")["lines_stopped"]}
    assert lines["line-a"]["cost_eur"] == (8 + 12) * 15_000
    assert lines["line-b"]["cost_eur"] == 8 * 15_000
    assert lines["line-c"]["hours_stopped"] == 3.03 and lines["line-c"]["cost_eur"] == 45_500


def test_each_response_states_what_it_leaves_within_reach(result):
    assert option(result)["lines_still_reachable"] == ["line-a", "line-b", "line-c"]
    assert option(result, "cut-cell-b2")["lines_still_reachable"] == ["line-a", "line-b", "line-c"]
    assert option(result, "cut-link-dmz-ot")["lines_still_reachable"] == ["line-b", "line-c"]
    assert option(result, "cut-plant-ot")["lines_still_reachable"] == []
    assert option(result, "cut-cell-b2", "cut-link-dmz-ot")["lines_still_reachable"] == []
    assert option(result)["still_at_stake_eur"] == (3 * 48 + 12) * 15_000


def test_recommendation_is_the_cheapest_response_that_closes_every_path(result):
    assert result["assessments"][0]["recommended"] == ["cut-cell-b2", "cut-link-dmz-ot"]


def test_the_same_response_costs_more_once_line_c_is_running_again(result):
    incident = dict(result["incidents"][0], last_seen="2026-11-10T09:00:00Z")
    priced = response.price([p for p in load("plant.json")["isolation_points"] if p["id"] == "cut-plant-ot"],
                            incident, load("plant.json"), load("production.json"))
    assert priced["cost_eur"] == (8 + 12 + 8 + 8) * 15_000


def test_closing_the_link_longer_than_the_loaded_orders_last_stops_the_lines(result):
    plant = load("plant.json")
    point = copy.deepcopy(next(p for p in plant["isolation_points"] if p["id"] == "cut-link-dmz-ot"))
    point["hold_hours"] = 8
    priced = response.price([point], result["incidents"][0], plant, load("production.json"))
    hours = {l["line"]: (l["hours_stopped"], l["restart_hours"]) for l in priced["lines_stopped"]}
    assert hours == {"line-a": (2, 12), "line-b": (2, 0), "line-c": (2, 0)}
    assert priced["cost_eur"] == (2 + 12 + 2 + 2) * 15_000


def test_without_the_open_file_share_closing_the_link_protects_line_c(result):
    plant = load("plant.json")
    plant["connections"] = [c for c in plant["connections"] if c["id"] != "link-b2-c1"]
    point = next(p for p in plant["isolation_points"] if p["id"] == "cut-link-dmz-ot")
    priced = response.price([point], result["incidents"][0], plant, load("production.json"))
    assert priced["lines_still_reachable"] == ["line-b"]


# -- the Control Tower holds the action --------------------------------------
def test_isolation_is_held_for_the_accountable_owner_and_not_carried_out(gateway, result):
    assert [h["decision"] for h in result["held"]] == ["require_approval"] * 2
    assert all(h["rule"] == "P-007,P-008,P-009" and not h["executed"] for h in result["held"])
    assert not [e for e in gateway.tools.executed if e["tool"] == "network.isolate"]
    waiting = Approvals(gateway).pending()
    assert len(waiting) == 2 and {w["approver"] for w in waiting} == {"Head of OT Security"}


def test_only_the_owner_can_release_and_then_it_is_carried_out(gateway, result):
    approvals = Approvals(gateway)
    first, second = [w["seq"] for w in approvals.pending()]
    with pytest.raises(ApprovalError):
        approvals.release(first, "Chief Information Security Officer")
    assert not [e for e in gateway.tools.executed if e["tool"] == "network.isolate"]
    assert approvals.release(first, "Head of OT Security")["executed"]
    assert approvals.release(second, "Head of OT Security")["executed"]
    done = [e["call"]["isolation_point"] for e in gateway.tools.executed if e["tool"] == "network.isolate"]
    assert done == ["cut-cell-b2", "cut-link-dmz-ot"] and approvals.pending() == []


def test_no_sentinel_agent_can_write_to_a_controller(gateway):
    for agent in AGENTS:
        assert gateway.execute(agent, "plc.write", {"controller": "plc-b2-01", "command": "stop"})["decision"] == "deny"


def test_only_the_response_agent_may_even_ask_for_an_isolation(gateway):
    for agent in ("ot-asset-discovery", "ot-threat-correlation", "ot-briefing"):
        verdict = gateway.execute(agent, "network.isolate", {"isolation_point": "cut-plant-ot"})
        assert verdict["decision"] == "deny" and verdict["rule"] == "PERM-1"


def test_the_response_agent_cannot_publish_a_report_on_its_own(gateway):
    assert gateway.execute("ot-response", "report.write", {"report": "x"})["decision"] == "require_approval"


def test_every_step_is_in_the_audit_record_and_the_record_is_intact(gateway, result):
    records = gateway.audit.records()
    assert len(records) == 13 and gateway.audit.verify()[0]
    assert [r["agent_id"] for r in records] == (["ot-asset-discovery"] * 3 + ["ot-threat-correlation"] * 3
                                                + ["ot-response"] * 5 + ["ot-briefing"] * 2)
    assert [r["decision"] for r in records].count("allow") == 11


# -- agent 4: briefing -------------------------------------------------------
def test_the_page_states_the_decision_in_production_terms(result):
    page = result["pages"][0]
    assert "The recommended response costs EUR 120,000 in lost output" in page
    assert "would cost EUR 465,500" in page and "EUR 345,500 less" in page
    assert "waiting for the Head of OT Security" in page and "**(recommended)**" in page
    assert page.count("| Head of OT Security |") == 2


def test_the_page_labels_its_figures_and_says_what_it_is_not(result):
    page = result["pages"][0]
    assert "none is a measured loss" in page and page.count("Assumption") >= 6
    assert "no language model" in page and "designed, not built" in page
    assert all(noise in page for noise in NOISE)


def test_the_published_page_is_what_the_code_produces_today(result):
    assert (REPORTS / "incident-latest.md").read_text(encoding="utf-8") == result["pages"][0]
