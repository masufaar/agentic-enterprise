"""Prepared replies: what a scripted stand-in says in place of a model.

These are not a model and prove nothing about one. They exist so that the tests and
the sample pages run every time, without a key and without cost, and so the fixed
code around the model can be shown working: the tools, the refusals handed back, the
hand-in checks, the ladder, the held drafts, the page. Each scenario includes at
least one hand-in the harness does not accept, and its correction.
"""


def ask(name: str, **given) -> dict:
    return {"tool_calls": [{"id": f"call-{name}", "name": name, "input": given}]}


MONITOR_HALT = [
    ask("read_event"),
    ask("trace_exposure", kind="supplier", id="SUP-NORD"),
    ask("read_part", part="PCM-7"),
    # a first hand-in the harness does not accept: it names no product a trace returned
    ask("file_exposure", material="yes", kind="stoppage", affected_products=[], revenue_at_risk_eur=1143000,
        min_days_of_cover=12, confidence="high", assessment="Nordkamp has halted PCM-7.", lesson="x"),
    ask("file_exposure", material="yes", kind="stoppage",
        affected_products=["PRD-A", "PRD-B", "PRD-C", "PRD-F"], revenue_at_risk_eur=1143000, min_days_of_cover=12,
        confidence="high",
        assessment="Nordkamp has halted shipments of the single-source part PCM-7. It feeds four products with "
                   "EUR 1,143,000 of open orders, and cover is only 12 days, inside the 21-day buffer.",
        lesson="A halt at the single source of PCM-7 cascades to four products; 12 days of cover is the clock."),
]

SOURCING_HALT = [
    ask("read_exposure"),
    ask("list_alternates", part="PCM-7"),
    ask("draft_po", part="PCM-7", supplier="SUP-TORNA", qty=400, amount_eur=21000,
        reason="Qualified second source for PCM-7 to bridge the gap before cover runs out."),
    ask("draft_supplier_email", to="orders@tornelis.example", subject="Urgent: PCM-7 demand",
        body="We need to bring forward PCM-7 volume. Please confirm your earliest lead time and price."),
    ask("propose_response",
        recommendation="Ranked: 1) qualified PO to Tornelis (held for sign-off), the only qualified second source; "
                       "2) an email to Tornelis to pull the lead time in; 3) recommend the Head of Supply Chain "
                       "re-allocate PCM-7 stock to the two highest-revenue orders. Do not use the unqualified "
                       "supplier.",
        options=["Qualified PO to Tornelis, EUR 21,000, lead 70 days (held)",
                 "Supplier email to Tornelis to shorten lead (held)",
                 "Re-allocate stock to CO-001 and CO-003 (recommended; a person decides)"],
        lesson="The qualified second source is slower and dearer, but it is the only one an agent may draft."),
]

MONITOR_TARIFF = [
    ask("read_event"),
    ask("trace_exposure", kind="part", id="HSG-4"),
    ask("file_exposure", material="yes", kind="cost",
        affected_products=["PRD-A", "PRD-C", "PRD-D", "PRD-F"], revenue_at_risk_eur=1116000, min_days_of_cover=50,
        confidence="medium",
        assessment="A 25% tariff raises the landed cost of HSG-4, used by four products. It is a cost, not a "
                   "stoppage: cover is 50 days and supply still flows.",
        lesson="A tariff is a cost exposure, not a stoppage; the response is price, not speed."),
]

SOURCING_TARIFF = [
    ask("read_exposure"),
    ask("list_alternates", part="HSG-4"),
    ask("draft_po", part="HSG-4", supplier="SUP-RHEIN", qty=5000, amount_eur=18000,
        reason="Qualified second source for HSG-4 to cap the tariff cost; held for sign-off."),
    ask("propose_response",
        recommendation="Ranked: 1) a qualified PO to Rheinwerk for HSG-4 at a lower landed cost (held for sign-off); "
                       "2) an email to Valoria to re-open terms. No speed is needed; cover is 50 days.",
        options=["Qualified PO to Rheinwerk, EUR 18,000 (held)", "Re-open terms with Valoria (recommended)"],
        lesson="For a cost exposure the clock is the tariff date, not the days of cover."),
]

MONITOR_FALSE = [
    ask("read_event"),
    ask("search_events", kind="supplier", about="SUP-TORNA", verified=True),
    # a first hand-in the harness does not accept: calling an unverified rumour material
    ask("file_exposure", material="yes", kind="stoppage", affected_products=["PRD-A"], revenue_at_risk_eur=0,
        min_days_of_cover=70, confidence="low", assessment="Tornelis may be insolvent.", lesson="x"),
    ask("file_exposure", material="no", kind="watch", confidence="low",
        assessment="An unverified rumour about Tornelis, a qualified alternate, not a primary supplier. No filing, "
                   "statement or second source. Not material until a second source confirms it.",
        lesson="A rumour is not an event; do not drop a qualified second source on a social-media post."),
]

REPLIES = {
    "single-source-halt": MONITOR_HALT + SOURCING_HALT,
    "tariff-cost": MONITOR_TARIFF + SOURCING_TARIFF,
    "false-alarm": MONITOR_FALSE,  # the response step is skipped: no material exposure
}
