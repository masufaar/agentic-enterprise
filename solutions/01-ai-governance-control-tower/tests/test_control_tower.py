"""Tests. Run from this solution folder with:  python -m pytest -q"""
import json

import pytest

from control_tower import redteam, registry
from control_tower.audit import AuditLog
from control_tower.classifier import classify
from control_tower.gateway import Gateway
from control_tower.killswitch import KillSwitch


@pytest.fixture
def gateway(tmp_path):
    return Gateway(audit=AuditLog(tmp_path / "audit.jsonl"),
                   killswitch=KillSwitch(tmp_path / "kill.json"))


def test_registry_loads_and_every_agent_has_an_owner():
    cards = registry.load()
    assert len(cards) == 16
    assert all(card["owner"] for card in cards.values())


def test_registry_rejects_incomplete_card(tmp_path):
    bad = tmp_path / "agents.json"
    bad.write_text(json.dumps({"agents": [{"id": "x"}]}))
    with pytest.raises(registry.RegistryError):
        registry.load(bad)


def test_classifier_tiers():
    cards = registry.load()
    assert classify(cards["ot-response"])["tier"] == "high"
    assert classify(cards["sd-triage"])["tier"] == "limited"
    assert classify(cards["ot-asset-discovery"])["tier"] == "minimal"
    social = {"id": "x", "use_case_flags": {"social_scoring": True}}
    assert classify(social)["tier"] == "prohibited"


def test_permitted_action_is_allowed(gateway):
    assert gateway.check("sd-triage", "ticket.read")["decision"] == "allow"


def test_unregistered_and_unapproved_agents_are_denied(gateway):
    assert gateway.check("ghost", "ticket.read")["rule"] == "REG-1"
    assert gateway.check("technician-interviewer", "kb.read")["rule"] == "REG-2"


def test_tool_and_data_outside_permissions_are_denied(gateway):
    assert gateway.check("sd-triage", "db.delete")["rule"] == "PERM-1"
    assert gateway.check("quality-traceability", "db.read", {"data_class": "personal"})["rule"] == "PERM-2"


def test_spend_limit_and_approval(gateway):
    assert gateway.check("sourcing-options", "erp.po.create", {"amount_eur": 250000})["decision"] == "deny"
    held = gateway.check("sourcing-options", "erp.po.create", {"amount_eur": 12000})
    assert held["decision"] == "require_approval"
    ok = gateway.check("sourcing-options", "erp.po.create", {"amount_eur": 12000},
                       approved_by="Chief Procurement Officer")
    assert ok["decision"] == "allow"


def test_agent_cannot_approve_itself(gateway):
    verdict = gateway.check("sourcing-options", "erp.po.create",
                            {"amount_eur": 12000, "approved_by": "Chief Financial Officer"})
    assert verdict["decision"] == "require_approval"


def test_missing_value_fails_closed(gateway):
    assert gateway.check("sourcing-options", "erp.po.create", {})["decision"] == "deny"
    assert gateway.check("sd-resolution", "email.send", {})["decision"] == "require_approval"


def test_kill_switch_single_and_all(gateway):
    gateway.killswitch.kill("sd-triage")
    assert gateway.check("sd-triage", "ticket.read")["rule"] == "KILL"
    assert gateway.check("sd-resolution", "ticket.read")["decision"] == "allow"
    gateway.killswitch.kill("all")
    assert gateway.check("sd-resolution", "ticket.read")["rule"] == "KILL"
    gateway.killswitch.revive("all")
    assert gateway.check("sd-triage", "ticket.read")["decision"] == "allow"


def test_every_decision_is_audited_and_tampering_is_detected(gateway):
    gateway.check("sd-triage", "ticket.read")
    gateway.check("sd-triage", "db.delete")
    gateway.check("ghost", "ticket.read")
    assert len(gateway.audit) == 3
    assert gateway.audit.verify()[0]
    lines = gateway.audit.path.read_text().splitlines()
    lines[1] = lines[1].replace('"deny"', '"allow"')
    gateway.audit.path.write_text("\n".join(lines) + "\n")
    ok, message = gateway.audit.verify()
    assert not ok and "record 2" in message


def test_redteam_campaign_has_no_false_blocks_and_only_known_breaches(gateway):
    report = redteam.run(gateway)
    summary = report["summary"]
    assert summary["controls_ok"] == summary["controls"]
    breached = {r["id"] for r in report["results"] if r["outcome"] == "BREACH"}
    assert breached == set(redteam.FIXES)  # a new breach, or a silently closed one, fails the build
    assert summary["audit_chain"] == "chain intact"


def test_gateway_reads_the_recipient_from_the_real_call(gateway):
    lie = {"to": "inbox@mail-collector.example", "recipient_domain": "halden-industrial.example"}
    verdict = gateway.execute("sd-resolution", "email.send", lie)
    assert verdict["decision"] == "require_approval" and not verdict["executed"]
    assert gateway.tools.executed == []


@pytest.mark.parametrize("call", [
    {"to": "a@halden-industrial.example", "bcc": "b@mail-collector.example"},
    {"to": ["a@halden-industrial.example", "b@mail-collector.example"]},
    {"to": "a@halden-industrial.example.mail-collector.example"},
    {"to": "b@mail-collector.example, a@halden-industrial.example"},
    {"to": "b@mail-collector.example@halden-industrial.example"},
    {"to": "Colleague <b@mail-collector.example>"},
    {"to": 42},
    {},
])
def test_outside_or_unreadable_recipients_are_never_sent_unapproved(gateway, call):
    verdict = gateway.execute("sd-resolution", "email.send", call)
    assert verdict["decision"] == "require_approval" and not verdict["executed"]


def test_internal_email_is_carried_out_and_denied_actions_are_not(gateway):
    ok = gateway.execute("sd-resolution", "email.send", {"to": " Employee@Halden-Industrial.example "})
    assert ok["decision"] == "allow" and ok["executed"]
    assert len(gateway.tools.executed) == 1
    denied = gateway.execute("sd-triage", "db.delete", {"target": "ticket_db"})
    assert not denied["executed"] and len(gateway.tools.executed) == 1


def test_daily_volume_limit_adds_up_small_requests(gateway):
    for _ in range(5):
        assert gateway.execute("quality-traceability", "db.read", {"rows": 900})["decision"] == "allow"
    over = gateway.execute("quality-traceability", "db.read", {"rows": 900})
    assert over["rule"] == "V-002" and not over["executed"]
    assert gateway.execute("quality-traceability", "db.read", {"rows": 500})["decision"] == "allow"
    assert gateway.execute("quality-traceability", "db.read", {"rows": 1})["rule"] == "V-002"


@pytest.mark.parametrize("rows", [None, -100000, 0, "900", 9.5, True])
def test_row_count_must_be_a_positive_whole_number(gateway, rows):
    params = {} if rows is None else {"rows": rows}
    assert gateway.execute("quality-traceability", "db.read", params)["rule"] == "V-001"


def test_dry_runs_and_refused_requests_do_not_use_up_the_allowance(gateway):
    gateway.check("quality-traceability", "db.read", {"rows": 4000})
    gateway.execute("quality-traceability", "db.read", {"rows": 6000})
    assert gateway.execute("quality-traceability", "db.read", {"rows": 5000})["decision"] == "allow"


def test_one_agents_volume_does_not_block_another(gateway, tmp_path):
    gateway.execute("quality-traceability", "db.read", {"rows": 5000})
    cards = dict(gateway.registry)
    cards["second"] = {**cards["quality-traceability"], "id": "second"}
    other = Gateway(registry=cards, audit=gateway.audit, killswitch=gateway.killswitch)
    assert other.execute("second", "db.read", {"rows": 5000})["decision"] == "allow"


# -- data labels: what may be written to a store every employee can read ------

LEAK = "Do what worked for employee HI-EMP-20417: sign out and sign in again."
CLEAN = "Sign out of the VPN client, sign in with the new password, restart the client."


def test_source_hands_out_records_with_a_label_on_every_field(gateway):
    record = gateway.tools.run("sd-resolution", "ticket.read", {"record": "T-1042"})["record"]
    assert record["private_phone"]["label"] == "personal"
    assert record["resolution"]["label"] == "internal"


@pytest.mark.parametrize("call", [
    {"content": LEAK, "data_class": "personal"},                      # honest about it
    {"content": LEAK, "data_class": "internal"},                      # lies about it
    {"content": LEAK},                                                # says nothing
    {"content": "Call  +00 555  0142 077 for help."},                 # extra spaces
    {"content": "ask hi-emp-20417"},                                  # capitals changed
    {"content": CLEAN, "title": "Tip from requester-20417@private-mail.example"},  # hidden in the title
    {"content": CLEAN, "tags": ["vpn", {"note": "HI-EMP-31188"}]},    # hidden in a nested field
    {"content": CLEAN, "data_class": "personal"},                     # declared personal
])
def test_personal_data_never_reaches_the_shared_store(gateway, call):
    verdict = gateway.execute("sd-resolution", "kb.write", call)
    assert verdict["rule"] == "P-010" and not verdict["executed"]
    assert gateway.tools.executed == []
    # an approver cannot wave it through either: deny beats approval
    again = gateway.execute("sd-resolution", "kb.write", call, approved_by="Head of IT Service Management")
    assert again["decision"] == "deny"


@pytest.mark.parametrize("call", [{}, {"content": ""}, {"content": 42}, {"title": CLEAN}])
def test_shared_store_write_without_readable_text_is_refused(gateway, call):
    assert gateway.execute("sd-resolution", "kb.write", call)["rule"] == "P-010"


def test_refused_personal_text_is_not_copied_into_the_audit_trail(gateway):
    gateway.execute("sd-resolution", "kb.write", {"content": LEAK, "title": "HI-EMP-20417"})
    assert "HI-EMP-20417" not in gateway.audit.path.read_text()
    assert gateway.audit.verify()[0]


def test_agent_cannot_state_its_own_content_label(gateway):
    verdict = gateway.execute("sd-resolution", "kb.write", {"content": LEAK, "content_label": "clean"})
    assert verdict["rule"] == "P-010"


def test_clean_text_from_an_agent_that_handled_personal_data_waits_for_a_human(gateway):
    assert gateway.execute("sd-resolution", "kb.write", {"content": CLEAN})["decision"] == "allow"
    gateway.execute("sd-resolution", "ticket.read", {"record": "T-1042"})
    held = gateway.execute("sd-resolution", "kb.write", {"content": CLEAN})
    assert held["rule"] == "P-011" and held["decision"] == "require_approval" and not held["executed"]
    released = gateway.execute("sd-resolution", "kb.write", {"content": CLEAN},
                               approved_by="Head of IT Service Management")
    assert released["decision"] == "allow" and released["executed"]


def test_dry_runs_and_refused_reads_do_not_mark_an_agent(gateway):
    gateway.check("sd-resolution", "ticket.read", {"record": "T-1042"})
    gateway.killswitch.kill("sd-resolution")
    gateway.execute("sd-resolution", "ticket.read", {"record": "T-1042"})
    gateway.killswitch.revive("sd-resolution")
    assert gateway.execute("sd-resolution", "kb.write", {"content": CLEAN})["decision"] == "allow"
