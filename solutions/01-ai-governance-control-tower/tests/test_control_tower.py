"""Tests. Run from this solution folder with:  python -m pytest -q"""
import json
import re

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
    assert len(cards) == 20
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
    assert gateway.execute("sd-resolution", "email.send", {})["decision"] == "require_approval"
    assert gateway.check("sd-resolution", "email.send", {})["decision"] == "deny"  # dry run with nothing stated


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


# -- data labels in email: who would read it ---------------------------------

LIST = "all-staff@halden-industrial.example"
SUBJECT = "employee@halden-industrial.example"       # HI-EMP-20417, the person the data is about
OTHER = "colleague@halden-industrial.example"        # a different employee
OWNER = "Head of IT Service Management"


@pytest.mark.parametrize("call", [
    {"to": LIST, "body": LEAK},
    {"to": SUBJECT, "bcc": LIST, "body": LEAK},                       # list hidden in blind copy
    {"to": [SUBJECT, "plant-03-office@halden-industrial.example"], "body": LEAK},
    {"to": LIST, "subject": "about HI-EMP-20417", "body": CLEAN},     # hidden in the subject line
    {"to": LIST, "body": CLEAN, "attachment": {"name": "hi-emp-20417.txt"}},
    {"to": "somebody-else@halden-industrial.example", "body": LEAK},  # internal, but not in the directory
    {"to": "inbox@mail-collector.example", "body": LEAK},             # outside the company
    {"body": LEAK},                                                   # no recipient stated
    {"to": LIST, "body": LEAK, "email_label": "ok"},                  # agent states its own label
])
def test_personal_data_is_never_emailed_to_many_or_unknown_readers(gateway, call):
    verdict = gateway.execute("sd-resolution", "email.send", call)
    assert verdict["rule"] == "P-012" and not verdict["executed"]
    assert gateway.execute("sd-resolution", "email.send", call, approved_by=OWNER)["decision"] == "deny"
    assert "HI-EMP-20417" not in gateway.audit.path.read_text().replace("hi-emp-20417.txt", "")
    assert gateway.tools.executed == []


def test_employee_may_be_sent_their_own_data_but_not_somebody_elses(gateway):
    own = gateway.execute("sd-resolution", "email.send", {"to": SUBJECT, "body": LEAK})
    assert own["decision"] == "allow" and own["executed"]
    other = gateway.execute("sd-resolution", "email.send", {"to": OTHER, "body": LEAK})
    assert other["rule"] == "P-013" and other["decision"] == "require_approval" and not other["executed"]
    both = gateway.execute("sd-resolution", "email.send", {"to": SUBJECT, "cc": OTHER, "body": LEAK})
    assert both["rule"] == "P-013"
    mixed = "HI-EMP-20417 and HI-EMP-31188 had the same fault."       # two people's data, one reader
    assert gateway.execute("sd-resolution", "email.send", {"to": SUBJECT, "body": mixed})["rule"] == "P-013"


def test_mail_to_a_list_from_an_agent_that_handled_personal_data_waits_for_a_human(gateway):
    notice = {"to": LIST, "body": CLEAN}
    assert gateway.execute("sd-resolution", "email.send", notice)["decision"] == "allow"
    gateway.execute("sd-resolution", "ticket.read", {"record": "T-1042"})
    held = gateway.execute("sd-resolution", "email.send", notice)
    assert held["rule"] == "P-013" and not held["executed"]
    assert gateway.execute("sd-resolution", "email.send", notice, approved_by=OWNER)["executed"]
    # an ordinary reply to one known employee is not held
    assert gateway.execute("sd-resolution", "email.send", {"to": OTHER, "body": CLEAN})["decision"] == "allow"


# -- approval queue -----------------------------------------------------------

from control_tower.approvals import ApprovalError, Approvals, page

CPO = "Chief Procurement Officer"


def test_held_request_appears_in_the_queue_with_its_approver_and_reason(gateway):
    held = gateway.execute("sourcing-options", "erp.po.create", {"amount_eur": 12000})
    gateway.execute("sd-triage", "ticket.read")          # allowed: not in the queue
    gateway.execute("sd-triage", "db.delete")            # denied: not in the queue
    gateway.check("sourcing-options", "erp.po.create", {"amount_eur": 12000})  # dry run: not in the queue
    (item,) = Approvals(gateway).pending()
    assert item["seq"] == held["audit_seq"] and item["approver"] == CPO
    assert "P-005" in item["rules"] and item["request"]["amount_eur"] == 12000


def test_release_by_the_owner_carries_the_action_out_and_empties_the_queue(gateway):
    held = gateway.execute("sourcing-options", "erp.po.create", {"amount_eur": 12000})
    approvals = Approvals(gateway)
    verdict = approvals.release(held["audit_seq"], CPO)
    assert verdict["decision"] == "allow" and verdict["executed"]
    assert approvals.pending() == [] and len(gateway.tools.executed) == 1
    with pytest.raises(ApprovalError):                   # cannot be released twice
        approvals.release(held["audit_seq"], CPO)
    assert len(gateway.tools.executed) == 1
    assert gateway.audit.verify()[0]


def test_only_the_accountable_owner_can_decide(gateway):
    held = gateway.execute("sourcing-options", "erp.po.create", {"amount_eur": 12000})
    approvals = Approvals(gateway)
    for action in (approvals.release, approvals.refuse):
        with pytest.raises(ApprovalError):
            action(held["audit_seq"], "Head of IT Service Management")
    assert gateway.tools.executed == [] and len(approvals.pending()) == 1
    assert gateway.audit.records()[-1]["decision"] == "rejected"   # the attempt is on record
    # and the gateway itself does not accept another role's approval either
    direct = gateway.execute("sourcing-options", "erp.po.create", {"amount_eur": 12000},
                             approved_by="Head of IT Service Management")
    assert direct["decision"] == "require_approval" and not direct["executed"]


def test_refusal_is_recorded_and_nothing_is_carried_out(gateway):
    held = gateway.execute("sourcing-options", "erp.po.create", {"amount_eur": 12000})
    approvals = Approvals(gateway)
    approvals.refuse(held["audit_seq"], CPO, "Supplier not on the approved list")
    assert approvals.pending() == [] and gateway.tools.executed == []
    (item,) = approvals.decided()
    assert item["outcome"]["decision"] == "refused" and "approved list" in item["outcome"]["reason"]


def test_release_is_decided_again_and_fails_if_the_kill_switch_was_pulled(gateway):
    held = gateway.execute("sourcing-options", "erp.po.create", {"amount_eur": 12000})
    gateway.killswitch.kill("sourcing-options")
    verdict = Approvals(gateway).release(held["audit_seq"], CPO)
    assert verdict["rule"] == "KILL" and not verdict["executed"]


def test_release_cannot_wave_through_what_the_rules_refuse(gateway):
    gateway.execute("sd-resolution", "ticket.read", {"record": "T-1042"})
    held = gateway.execute("sd-resolution", "email.send", {"to": LIST, "body": CLEAN})
    # the held text is tampered with after the fact: the audit check catches that
    lines = gateway.audit.path.read_text().splitlines()
    lines[-1] = lines[-1].replace("Sign out", "HI-EMP-20417 sign out")
    gateway.audit.path.write_text("\n".join(lines) + "\n")
    assert not gateway.audit.verify()[0]
    # and even then the gateway reads the text again on release and refuses it
    verdict = Approvals(gateway).release(held["audit_seq"], OWNER)
    assert verdict["rule"] == "P-012" and not verdict["executed"]


def test_approver_is_told_what_to_look_for(gateway):
    gateway.execute("sd-resolution", "ticket.read", {"record": "T-1042"})
    gateway.execute("sd-resolution", "email.send", {"to": OTHER, "body": LEAK})
    gateway.execute("sd-resolution", "kb.write", {"content": CLEAN})
    gateway.execute("sd-resolution", "email.send", {"to": "inbox@mail-collector.example"})
    other, article, outside = Approvals(gateway).pending()
    assert any("personal data of HI-EMP-20417: employee number" in h for h in other["look_for"])
    assert any("T-1042" in h for h in article["look_for"])
    assert any("mail-collector.example" in h for h in outside["look_for"])
    text = page(Approvals(gateway))
    assert "3 items waiting" in text and "Head of IT Service Management | 3" in text
    assert "## Waiting 3 of 3:" in text and f"- **Audit record:** {outside['seq']}" in text
    assert "`inbox@mail-collector.example`" in text   # shown as text, not as a mail link


def test_page_marks_a_forged_approval_and_an_empty_request(gateway):
    gateway.execute("sourcing-options", "erp.po.create",
                    {"amount_eur": 24000, "approved_by": "Chief Financial Officer"})
    gateway.execute("sd-resolution", "email.send", {"data_class": "personal"})
    forged, empty = Approvals(gateway).pending()
    assert any("claims an approval by Chief Financial Officer" in h for h in forged["look_for"])
    text = page(Approvals(gateway))
    assert "the agent stated no details" in text and "(nothing stated)" not in text


def test_decided_items_no_longer_say_waiting(gateway):
    held = gateway.execute("sourcing-options", "erp.po.create", {"amount_eur": 12000})
    Approvals(gateway).release(held["audit_seq"], CPO)
    text = page(Approvals(gateway))
    assert "## Decided 1 of 1:" in text and "- **Approver:** " + CPO in text
    assert "Waiting for:" not in text and "Why it was held" in text


def test_results_page_lists_cases_in_order_of_id(gateway, tmp_path, monkeypatch):
    monkeypatch.setattr(redteam, "REPORTS", tmp_path)
    redteam.publish(redteam.run(gateway))
    ids = re.findall(r"^\| ([AC]-\d+) ", (tmp_path / "redteam-latest.md").read_text(), re.M)
    assert ids == sorted(ids) and len(ids) == 37


def test_campaign_sends_legitimate_requests_through_the_queue(gateway):
    report = redteam.run(gateway)
    approvals = Approvals(gateway)
    assert len(approvals.pending()) == report["summary"]["held_for_human"]
    assert len(approvals.decided()) == 3 and all(
        item["outcome"]["decision"] == "allow" for item in approvals.decided())


# --- board report -------------------------------------------------------------
from control_tower import board


def test_board_page_answers_in_plain_words(gateway):
    report = redteam.run(gateway)
    text = board.page(report)
    assert "| Is the record of decisions unaltered? | Yes. " in text and "chain intact" not in text
    assert "It may read on its own" in text and "They may read" not in text   # one high-risk agent
    report["summary"]["audit_chain"] = "chain broken at record 5"
    assert "| **No.** The check failed (chain broken at record 5)." in board.page(report)


def test_board_figures_count_every_agent_once_by_tier(gateway):
    f = board.figures(redteam.run(gateway))
    assert sum(len(cards) for cards in f["by_tier"].values()) == f["agents"] == 20
    assert sum(f["by_autonomy"].values()) == 20
    assert len(f["approved"]) + len(f["not_approved"]) == 20


def test_board_pass_rate_counts_refused_held_and_capped_as_contained(gateway):
    report = redteam.run(gateway)
    f, s = board.figures(report), report["summary"]
    assert f["contained"] == s["blocked"] + s["held_for_human"] + s["capped"]
    assert f["contained"] + len(f["breaches"]) == f["attacks"] == s["attacks"]


def test_board_page_names_every_open_finding_with_its_fix(gateway):
    report = redteam.run(gateway)
    text = board.page(report, redteam.FIXES)
    for r in report["results"]:
        if r["outcome"] == "BREACH":
            assert f"Open finding {r['id']}" in text and redteam.FIXES[r["id"]] in text


def test_board_page_reports_a_breach_free_campaign_without_inventing_findings(gateway):
    report = redteam.run(gateway)
    report["results"] = [r for r in report["results"] if r["outcome"] != "BREACH"]
    assert "Open finding" not in board.page(report, redteam.FIXES)


def test_board_page_flags_load_on_one_approver_and_agents_not_approved(gateway):
    report = redteam.run(gateway)
    text = board.page(report, redteam.FIXES)
    top = max(report["waiting_by_approver"].values())
    assert f"{top} of {sum(report['waiting_by_approver'].values())} waiting actions fall on one role" in text
    assert "Registered but not approved" in text
    assert sum(report["waiting_by_approver"].values()) == report["summary"]["held_for_human"]


def test_board_page_shows_agents_that_are_switched_off(gateway):
    report = redteam.run(gateway)
    assert "| How many are switched off right now? | 1 |" in board.page(report, stopped=["sd-triage"])
    assert "| How many are switched off right now? | all |" in board.page(report, stopped=["all"])


# -- reach of action and what stands behind a card ------------------------------
def test_reach_is_rated_from_the_permission_list_highest_level_first():
    from control_tower.reach import level_of, reach
    cards = registry.load()
    assert [level_of(t) for t in ("erp.read", "twin.simulate", "report.write", "erp.plan.propose", "ticket.update",
                                  "email.send", "identity.account.suspend", "erp.po.create",
                                  "network.isolate", "plc.write")] == [1, 1, 2, 2, 2, 3, 3, 3, 4, 4]
    assert reach(cards["ot-response"])["level"] == 4 and reach(cards["ot-response"])["because"] == ["network.isolate"]
    assert reach(cards["ot-challenger"]) == {"agent_id": "ot-challenger", "level": 1, "name": "Reads only",
                                             "because": [], "on_its_own": False, "signed_off_by": None}


def test_a_tool_nobody_has_classified_counts_as_an_action():
    from control_tower.reach import level_of
    assert level_of("payroll.adjust") == 3


def test_the_legal_tier_and_the_reach_can_disagree_and_the_board_page_says_so(gateway):
    from control_tower.reach import reach
    card = registry.load()["ot-first-response"]
    assert classify(card)["tier"] == "minimal"
    assert reach(card)["level"] == 3 and reach(card)["on_its_own"]
    report = redteam.run(gateway)
    f = board.figures(report)
    assert "ot-first-response" in [c["id"] for c in f["far_on_their_own"]]
    assert "ot-response" not in [c["id"] for c in f["far_on_their_own"]]  # level 4, but never without a person
    text = board.page(report)
    assert "**Acting on their own beyond reading and writing.** Office-side First Response Agent" in text
    assert "| 4: Can stop production | 1 | 0 | OT Incident Containment Assistant |" in text


def test_board_figures_count_every_card_once_by_reach_and_by_what_stands_behind_it(gateway):
    f = board.figures(redteam.run(gateway))
    assert sum(len(cards) for cards in f["by_reach"].values()) == 20
    assert f["today"] == {"designed": 11, "fixed code": 6, "agent in build": 0, "agent working": 3}
    text = board.page(redteam.run(gateway))
    assert "3 agents working; 6 steps of fixed code without a model; 11 designed agents" in text
    assert "No agent is rated working yet." not in text


def test_a_card_must_say_what_stands_behind_it(tmp_path):
    cards = json.loads((registry.DATA / "agents.json").read_text(encoding="utf-8"))["agents"][:1]
    cards[0]["today"] = "almost done"
    bad = tmp_path / "agents.json"
    bad.write_text(json.dumps({"agents": cards}))
    with pytest.raises(registry.RegistryError, match="unknown state today"):
        registry.load(bad)
