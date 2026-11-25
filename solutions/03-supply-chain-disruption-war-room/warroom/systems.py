"""Stand-ins for the two systems Halden already runs.

In a company these are the real systems, reached through their own supported
connections (a risk feed and an ERP both offer one to an outside agent). Here they
are fixed code over synthetic files, under invented vendor names:

  Feed   Larkspur Supply Signals: the risk feed Halden subscribes to. It publishes
         events (supplier news, tariffs, ports, weather, supplier finances). It is
         the detection market; this solution consumes it, it does not rebuild it.
  ERP    Fenmark MRP: the system of record for the bill of materials, inventory,
         open purchase orders and open customer orders.

No real system is connected. The BOM traversal (erp.trace) is a deterministic graph
walk from a part or a supplier to the products, open orders and revenue it touches:
fixed code, a tool, not an agent. Nothing here forecasts anything.
"""
from . import ERP_NAME, FEED_NAME, load
from harness.loop import ToolProblem


class SystemProblem(ToolProblem):
    """A system could not do what was asked. An agent is told why and can try something else."""


class Feed:
    name = FEED_NAME

    def __init__(self, events: dict | None = None):
        source = events or load("events.json")
        self.as_of = source["as_of"]
        self.events = {e["id"]: dict(e) for e in source["events"]}

    def event(self, event_id: str) -> dict:
        if event_id not in self.events:
            raise SystemProblem(f"There is no event {event_id} on the feed.")
        return self.events[event_id]

    def search(self, type: str | None = None, kind: str | None = None, about: str | None = None,
               verified: bool | None = None, limit: int = 25) -> list[dict]:
        found = [e for e in self.events.values()
                 if (type is None or e["type"] == type)
                 and (kind is None or e["about"]["kind"] == kind)
                 and (about is None or e["about"]["id"] == about)
                 and (verified is None or e["verified"] == verified)]
        found.sort(key=lambda e: e["date"])
        return [{k: e[k] for k in ("id", "date", "type", "about", "severity", "verified", "headline")}
                for e in found[:limit]]


class ERP:
    name = ERP_NAME

    def __init__(self, parts: dict | None = None, suppliers: dict | None = None,
                 inventory: dict | None = None, orders: dict | None = None, alternates: dict | None = None):
        p = parts or load("parts.json")
        self.as_of = p["as_of"]
        self.parts = p["parts"]
        self.products = p["products"]
        self.suppliers = (suppliers or load("suppliers.json"))["suppliers"]
        self.inventory = (inventory or load("inventory.json"))["inventory"]
        o = orders or load("orders.json")
        self.customer_orders = {c["id"]: dict(c) for c in o["customer_orders"]}
        self.purchase_orders = {po["id"]: dict(po) for po in o["purchase_orders"]}
        self._alternates = (alternates or load("alternates.json"))["alternates"]
        self.drafts: list[dict] = []       # POs and emails drafted through the connector, never sent
        self.reallocations: list[dict] = []

    # -- reading ---------------------------------------------------------------
    def part(self, part_id: str) -> dict:
        if part_id not in self.parts:
            raise SystemProblem(f"There is no part {part_id}.")
        return {"id": part_id, **self.parts[part_id], **self.inventory.get(part_id, {})}

    def supplier(self, supplier_id: str) -> dict:
        if supplier_id not in self.suppliers:
            raise SystemProblem(f"There is no supplier {supplier_id}.")
        return {"id": supplier_id, **self.suppliers[supplier_id]}

    def alternates(self, part_id: str) -> list[dict]:
        self.part(part_id)
        return [{**a, "supplier_name": self.suppliers.get(a["supplier"], {}).get("name", a["supplier"])}
                for a in self._alternates.get(part_id, [])]

    # -- the BOM walk ----------------------------------------------------------
    def _parts_of(self, about: dict) -> list[str]:
        """Which parts a feed event touches: a part is itself; a supplier is its parts;
        a region is the parts whose primary supplier sits in it."""
        kind, thing = about["kind"], about["id"]
        if kind == "part":
            return [thing] if thing in self.parts else []
        if kind == "supplier":
            direct = self.suppliers.get(thing, {}).get("supplies", [])
            primary = [pid for pid, p in self.parts.items() if p["primary_supplier"] == thing]
            return sorted(set(direct) | set(primary))
        if kind == "region":
            return sorted(pid for pid, p in self.parts.items()
                          if self.suppliers.get(p["primary_supplier"], {}).get("region") == thing)
        return []

    def products_using(self, part_ids: list[str]) -> list[str]:
        wanted = set(part_ids)
        return [pid for pid, prod in self.products.items()
                if any(line["part"] in wanted for line in prod["bom"])]

    def open_orders_for(self, product_ids: list[str]) -> list[dict]:
        wanted = set(product_ids)
        return [o for o in self.customer_orders.values() if o["product"] in wanted and o["status"] == "open"]

    def trace(self, about: dict) -> dict:
        """From a part, a supplier or a region to the exposure it creates: the affected
        parts, the products that use them, the open customer orders and the revenue at
        risk, with the least days of cover among the affected parts. Fixed code."""
        parts = self._parts_of(about)
        if not parts:
            return {"about": about, "affected_parts": [], "affected_products": [], "affected_orders": [],
                    "revenue_at_risk_eur": 0, "min_days_of_cover": None,
                    "note": "No part of Halden's bill of materials maps to this. It may be real, but it is not "
                            "ours: nothing to decide here."}
        products = self.products_using(parts)
        orders = self.open_orders_for(products)
        revenue = sum(o["revenue_eur"] for o in orders)
        covers = [self.inventory[p]["days_of_cover"] for p in parts if p in self.inventory]
        return {
            "about": about,
            "affected_parts": [{"id": p, "name": self.parts[p]["name"], "single_source": self.parts[p]["single_source"],
                                "days_of_cover": self.inventory.get(p, {}).get("days_of_cover")} for p in parts],
            "affected_products": [{"id": p, "name": self.products[p]["name"], "region": self.products[p]["region"]}
                                  for p in products],
            "affected_orders": [{k: o[k] for k in ("id", "product", "qty", "revenue_eur", "due", "customer", "region")}
                                for o in sorted(orders, key=lambda o: -o["revenue_eur"])],
            "revenue_at_risk_eur": revenue,
            "min_days_of_cover": min(covers) if covers else None,
            "note": "Revenue at risk is the sum of open customer orders for the affected products, from the ERP. "
                    "It is a measured figure of synthetic data, not a forecast."}

    # -- the money and allocation actions (drafted, never sent) ----------------
    def draft_po(self, actor: str, part: str, supplier: str, qty: int, amount_eur: int, reason: str) -> dict:
        self.part(part)
        self.supplier(supplier)
        draft = {"kind": "purchase_order", "by": actor, "part": part, "supplier": supplier, "qty": qty,
                 "amount_eur": amount_eur, "reason": reason, "status": "drafted, awaiting sign-off"}
        self.drafts.append(draft)
        return draft

    def draft_email(self, actor: str, to: str, subject: str, body: str) -> dict:
        draft = {"kind": "email", "by": actor, "to": to, "subject": subject, "body": body,
                 "status": "drafted, awaiting sign-off"}
        self.drafts.append(draft)
        return draft

    def reallocate(self, actor: str, part: str, from_order: str, to_order: str, qty: int, reason: str) -> dict:
        for order in (from_order, to_order):
            if order not in self.customer_orders:
                raise SystemProblem(f"There is no customer order {order}.")
        move = {"kind": "reallocation", "by": actor, "part": part, "from_order": from_order, "to_order": to_order,
                "qty": qty, "reason": reason, "status": "drafted, awaiting sign-off"}
        self.reallocations.append(move)
        return move
