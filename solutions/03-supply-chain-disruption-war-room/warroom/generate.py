"""Write the synthetic Halden data for the war room, from a fixed seed.

Deterministic: same seed, same files, every time. No model, no network. The data
is a small but complete manufacturing picture: a bill of materials, the suppliers
behind it, inventory and days of cover, open customer and purchase orders, the risk
feed, qualified alternatives, and an answer key the agents never see.

One part family is single-source on purpose (the power control module PCM-7, from
one supplier), so a single sub-tier event cascades to several products, as the
Nexperia case did in October 2025.
"""
import json

from . import DATA

AS_OF = "2026-02-13"

SUPPLIERS = {
    "SUP-NORD": {"name": "Nordkamp Semiconductors", "region": "Asia", "financial_health": "stable",
                 "supplies": ["PCM-7"], "lead_time_days": 56},
    "SUP-RHEIN": {"name": "Rheinwerk Components", "region": "Europe", "financial_health": "stable",
                  "supplies": ["SNS-2", "BRD-1"], "lead_time_days": 28},
    "SUP-VALO": {"name": "Valoria Metals", "region": "Europe", "financial_health": "stable",
                 "supplies": ["HSG-4"], "lead_time_days": 21},
    "SUP-TORNA": {"name": "Tornelis Electronics", "region": "Europe", "financial_health": "stable",
                  "supplies": ["CBL-3"], "lead_time_days": 35},
    "SUP-MEAD": {"name": "Meadowbrook Sensors", "region": "Americas", "financial_health": "watch",
                 "supplies": [], "lead_time_days": 42},
    "SUP-GREY": {"name": "Greywater Components", "region": "Asia", "financial_health": "unknown",
                 "supplies": [], "lead_time_days": 30},
}

PARTS = {
    "PCM-7": {"name": "Power Control Module PCM-7", "family": "power semiconductors",
              "primary_supplier": "SUP-NORD", "single_source": True, "unit_cost_eur": 38},
    "SNS-2": {"name": "Sensor Module SNS-2", "family": "sensors",
              "primary_supplier": "SUP-RHEIN", "single_source": False, "unit_cost_eur": 22},
    "BRD-1": {"name": "Control Board BRD-1", "family": "boards",
              "primary_supplier": "SUP-RHEIN", "single_source": False, "unit_cost_eur": 54},
    "HSG-4": {"name": "Aluminium Housing HSG-4", "family": "housings",
              "primary_supplier": "SUP-VALO", "single_source": False, "unit_cost_eur": 12},
    "CBL-3": {"name": "Cable Harness CBL-3", "family": "harnesses",
              "primary_supplier": "SUP-TORNA", "single_source": False, "unit_cost_eur": 9},
}

PRODUCTS = {
    "PRD-A": {"name": "Drive Unit HX-200", "region": "Europe",
              "bom": [{"part": "PCM-7", "qty": 1}, {"part": "BRD-1", "qty": 1}, {"part": "HSG-4", "qty": 1}]},
    "PRD-B": {"name": "Sensor Pack SP-50", "region": "Europe",
              "bom": [{"part": "PCM-7", "qty": 2}, {"part": "SNS-2", "qty": 3}]},
    "PRD-C": {"name": "Power Module PM-900", "region": "Americas",
              "bom": [{"part": "PCM-7", "qty": 1}, {"part": "HSG-4", "qty": 1}, {"part": "CBL-3", "qty": 2}]},
    "PRD-D": {"name": "Control Cabinet CC-12", "region": "Europe",
              "bom": [{"part": "BRD-1", "qty": 2}, {"part": "HSG-4", "qty": 1}]},
    "PRD-E": {"name": "Signal Router SR-7", "region": "Asia",
              "bom": [{"part": "SNS-2", "qty": 1}, {"part": "CBL-3", "qty": 1}]},
    "PRD-F": {"name": "Drive Unit HX-400", "region": "Americas",
              "bom": [{"part": "PCM-7", "qty": 1}, {"part": "BRD-1", "qty": 2}, {"part": "HSG-4", "qty": 2}]},
}

INVENTORY = {  # on_hand, daily_consumption; days_of_cover is derived
    "PCM-7": {"on_hand": 4800, "daily_consumption": 400},
    "SNS-2": {"on_hand": 9000, "daily_consumption": 300},
    "BRD-1": {"on_hand": 6000, "daily_consumption": 200},
    "HSG-4": {"on_hand": 11000, "daily_consumption": 220},
    "CBL-3": {"on_hand": 8000, "daily_consumption": 160},
}

CUSTOMER_ORDERS = [  # revenue_eur is derived from qty * unit_price_eur
    {"id": "CO-001", "product": "PRD-A", "qty": 20, "unit_price_eur": 18000, "due": "2026-03-16",
     "customer": "Aurora Rail", "region": "Europe"},
    {"id": "CO-002", "product": "PRD-B", "qty": 15, "unit_price_eur": 9000, "due": "2026-03-09",
     "customer": "Beltra Energy", "region": "Europe"},
    {"id": "CO-003", "product": "PRD-C", "qty": 8, "unit_price_eur": 42000, "due": "2026-03-20",
     "customer": "Cardinal Utilities", "region": "Americas"},
    {"id": "CO-004", "product": "PRD-F", "qty": 6, "unit_price_eur": 31000, "due": "2026-03-11",
     "customer": "Delmar Transit", "region": "Americas"},
    {"id": "CO-005", "product": "PRD-D", "qty": 12, "unit_price_eur": 12000, "due": "2026-03-25",
     "customer": "Evershed Metro", "region": "Europe"},
    {"id": "CO-006", "product": "PRD-E", "qty": 30, "unit_price_eur": 3000, "due": "2026-03-30",
     "customer": "Fjellstad Grid", "region": "Asia"},
    {"id": "CO-007", "product": "PRD-A", "qty": 5, "unit_price_eur": 18000, "due": "2026-03-13",
     "customer": "Granholm AG", "region": "Europe"},
    {"id": "CO-008", "product": "PRD-B", "qty": 4, "unit_price_eur": 9000, "due": "2026-03-18",
     "customer": "Haldor Shipping", "region": "Europe"},
]

PURCHASE_ORDERS = [
    {"id": "PO-001", "part": "PCM-7", "supplier": "SUP-NORD", "qty": 6000, "amount_eur": 228000, "due": "2026-03-02"},
    {"id": "PO-002", "part": "HSG-4", "supplier": "SUP-VALO", "qty": 5000, "amount_eur": 60000, "due": "2026-02-24"},
    {"id": "PO-003", "part": "SNS-2", "supplier": "SUP-RHEIN", "qty": 4000, "amount_eur": 88000, "due": "2026-03-04"},
    {"id": "PO-004", "part": "BRD-1", "supplier": "SUP-RHEIN", "qty": 2500, "amount_eur": 135000, "due": "2026-03-07"},
    {"id": "PO-005", "part": "CBL-3", "supplier": "SUP-TORNA", "qty": 3000, "amount_eur": 27000, "due": "2026-03-01"},
]

ALTERNATES = {
    "PCM-7": [
        {"supplier": "SUP-TORNA", "qualified": True, "lead_time_days": 70, "price_index": 1.40,
         "note": "Qualified second source (PPAP on file 2024). Longer lead, higher price."},
        {"supplier": "SUP-GREY", "qualified": False, "lead_time_days": 30, "price_index": 0.95,
         "note": "Not qualified: no PPAP, never audited. Cheaper and fast, but unapproved for PCM-7."},
    ],
    "SNS-2": [{"supplier": "SUP-MEAD", "qualified": True, "lead_time_days": 42, "price_index": 1.15,
               "note": "Qualified second source."}],
    "HSG-4": [{"supplier": "SUP-RHEIN", "qualified": True, "lead_time_days": 35, "price_index": 1.10,
               "note": "Qualified; Rheinwerk also tools housings."}],
    "CBL-3": [{"supplier": "SUP-RHEIN", "qualified": True, "lead_time_days": 40, "price_index": 1.05,
               "note": "Qualified second source."}],
}

EVENTS = [
    {"id": "EV-01", "date": "2025-10-27", "source": "Larkspur Supply Signals", "type": "supplier_halt",
     "about": {"kind": "supplier", "id": "SUP-NORD"}, "severity": "high", "verified": True,
     "headline": "Nordkamp halts shipments amid ownership dispute",
     "text": "Nordkamp Semiconductors has suspended wafer shipments from its main plant after a government "
             "intervention in its ownership. Delivery of its power control modules cannot be guaranteed."},
    {"id": "EV-02", "date": "2026-01-14", "source": "Larkspur Supply Signals", "type": "tariff",
     "about": {"kind": "part", "id": "HSG-4"}, "severity": "medium", "verified": True,
     "headline": "25% tariff announced on imported aluminium housings",
     "text": "A 25% import tariff on aluminium housings takes effect next month, raising the landed cost of HSG-4."},
    {"id": "EV-03", "date": "2026-02-03", "source": "Larkspur Supply Signals", "type": "port",
     "about": {"kind": "region", "id": "Europe"}, "severity": "medium", "verified": True,
     "headline": "Port congestion at Rotterdam, nine-day delays",
     "text": "Congestion at Rotterdam is adding about nine days to inbound European shipments."},
    {"id": "EV-04", "date": "2026-02-10", "source": "Larkspur Supply Signals", "type": "financial",
     "about": {"kind": "supplier", "id": "SUP-NORD"}, "severity": "medium", "verified": True,
     "headline": "Nordkamp parent credit rating downgraded",
     "text": "The parent of Nordkamp Semiconductors has been downgraded two notches by a rating agency."},
    {"id": "EV-05", "date": "2026-02-12", "source": "Larkspur Supply Signals", "type": "rumor",
     "about": {"kind": "supplier", "id": "SUP-TORNA"}, "severity": "high", "verified": False,
     "headline": "Unconfirmed: Tornelis facing insolvency",
     "text": "An unverified social-media post claims Tornelis Electronics is about to file for insolvency. No "
             "filing, statement or second source has been found."},
    {"id": "EV-06", "date": "2026-02-05", "source": "Larkspur Supply Signals", "type": "weather",
     "about": {"kind": "region", "id": "Americas"}, "severity": "low", "verified": True,
     "headline": "Storms forecast off the Gulf coast",
     "text": "A storm system may bring short delays to Gulf-coast freight next week."},
    {"id": "EV-07", "date": "2026-02-08", "source": "Larkspur Supply Signals", "type": "supplier_halt",
     "about": {"kind": "supplier", "id": "SUP-OTHER"}, "severity": "high", "verified": True,
     "headline": "Castwell Forgings stops a production line",
     "text": "Castwell Forgings has stopped a line after a fire. Castwell is not a supplier to Halden."},
    {"id": "EV-08", "date": "2026-02-11", "source": "Larkspur Supply Signals", "type": "financial",
     "about": {"kind": "supplier", "id": "SUP-MEAD"}, "severity": "low", "verified": True,
     "headline": "Meadowbrook Sensors reports a soft quarter",
     "text": "Meadowbrook Sensors, a qualified alternate for SNS-2 that Halden does not currently buy from, "
             "reported weaker quarterly results."},
]

# The ground truth the agents never see. 'material' means it touches Halden's own
# bill of materials or cost and needs a decision; the parts and products it truly hits.
ANSWER_KEY = {
    "EV-01": {"material": True, "kind": "stoppage", "hits_parts": ["PCM-7"],
              "hits_products": ["PRD-A", "PRD-B", "PRD-C", "PRD-F"],
              "note": "Single-source part from the halted supplier; four products depend on it."},
    "EV-02": {"material": True, "kind": "cost", "hits_parts": ["HSG-4"],
              "hits_products": ["PRD-A", "PRD-C", "PRD-D", "PRD-F"],
              "note": "A landed-cost rise on a part used by four products; not a stoppage."},
    "EV-03": {"material": True, "kind": "delay", "hits_parts": ["SNS-2", "BRD-1", "HSG-4", "CBL-3"],
              "hits_products": ["PRD-A", "PRD-B", "PRD-C", "PRD-D", "PRD-E", "PRD-F"],
              "note": "European inbound delay touches every European-sourced part; a delay, not a stoppage."},
    "EV-04": {"material": True, "kind": "watch", "hits_parts": ["PCM-7"],
              "hits_products": ["PRD-A", "PRD-B", "PRD-C", "PRD-F"],
              "note": "A financial-health signal on the single-source supplier; worth watching, not yet acting."},
    "EV-05": {"material": False, "kind": "rumor", "hits_parts": [], "hits_products": [],
              "note": "Unverified rumour about a qualified ALTERNATE, not a primary supplier. Acting on it would "
                      "wrongly drop a second source. Not material until a second source confirms it."},
    "EV-06": {"material": False, "kind": "noise", "hits_parts": [], "hits_products": [],
              "note": "Low-severity weather with no mapped part."},
    "EV-07": {"material": False, "kind": "noise", "hits_parts": [], "hits_products": [],
              "note": "A real stoppage at a company that is not a Halden supplier."},
    "EV-08": {"material": False, "kind": "noise", "hits_parts": [], "hits_products": [],
              "note": "A soft quarter at a supplier Halden does not currently buy from."},
}


def _days_of_cover(on_hand: int, daily: int) -> int:
    return on_hand // daily if daily else 10_000


def build() -> dict:
    parts = {"as_of": AS_OF, "parts": PARTS, "products": PRODUCTS}
    suppliers = {"as_of": AS_OF, "suppliers": SUPPLIERS}
    alternates = {"alternates": ALTERNATES}
    inventory = {"as_of": AS_OF, "inventory": {
        pid: {**v, "days_of_cover": _days_of_cover(v["on_hand"], v["daily_consumption"])}
        for pid, v in INVENTORY.items()}}
    orders = {"as_of": AS_OF,
              "customer_orders": [{**o, "revenue_eur": o["qty"] * o["unit_price_eur"], "status": "open"}
                                  for o in CUSTOMER_ORDERS],
              "purchase_orders": [{**p, "status": "open"} for p in PURCHASE_ORDERS]}
    events = {"as_of": AS_OF, "events": EVENTS}
    answer_key = {"as_of": AS_OF, "events": ANSWER_KEY}
    return {"parts.json": parts, "suppliers.json": suppliers, "alternates.json": alternates,
            "inventory.json": inventory, "orders.json": orders, "events.json": events,
            "answer-key.json": answer_key}


def write() -> list[str]:
    DATA.mkdir(parents=True, exist_ok=True)
    written = []
    for name, payload in build().items():
        (DATA / name).write_text(json.dumps(payload, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        written.append(name)
    return written


if __name__ == "__main__":
    print("Written: " + ", ".join(write()))
