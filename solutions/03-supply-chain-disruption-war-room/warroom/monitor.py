"""The Supplier Disruption Monitor: it maps one event onto the bill of materials.

One agent, one job, one event at a time. It reads the event and the public record,
judges whether the event touches Halden's own bill of materials, and if it does it
maps it: the affected parts, the products that use them, the open customer orders,
the revenue at risk and the least days of cover. It is a proposal, not an action.

It never changes anything, and it is given no tool that could. The controls live
here, in fixed code:
  - every tool call goes through the connector and the Control Tower under the
    monitor's own identity; its card holds no tool that moves money or supply;
  - a material exposure is accepted only after trace_exposure has been run, and
    every euro figure in the assessment must be one a tool returned in this run;
  - an unverified event may not be called material unless a second verified event
    about the same thing was returned by search_events in this run (a rumour is not
    an event);
  - a material exposure must name at least one affected product that a trace returned;
  - the confidence is stated, and every text stays within the briefing's limits.
"""
from harness import checks
from harness.loop import Tool, ToolProblem

from . import MONITOR

KINDS = ("stoppage", "cost", "delay", "watch", "not_material")
CONFIDENCE = ("high", "medium", "low")

ROLE = (
    "You are the supply chain disruption monitor at Halden Industrial. You are given one event from the risk feed. "
    "You decide whether it touches Halden's own bill of materials, and if it does you map it: which parts, which "
    "products, which open customer orders, and the revenue at risk. You read; you never change anything and you have "
    "no tool to. You do not forecast: you judge an event that has happened. An unverified rumour is not an event; do "
    "not call it material unless a second, verified source confirms it. Say what you do not know. Map the exposure "
    "with trace_exposure before you put a number on it; every figure you report must come from a tool. Finish with "
    "file_exposure. If it is not accepted, correct it and file again.")


def system(briefing: dict) -> str:
    parts = [
        ROLE, "COMPANY BRIEFING", briefing["company"],
        "What matters, in this order:\n" + "\n".join(f"{n}. {t}" for n, t in enumerate(briefing["what_matters_in_this_order"], 1)),
        f"Critical part families: {', '.join(briefing['critical_part_families'])}.",
        f"Risk appetite: {briefing['risk_appetite']}",
        f"Confirmations that count for an unverified event: {', '.join(briefing['confirmations_that_count'])}.",
        f"The buffer to beat is {briefing['buffer_days']} days of cover.",
        f"Who decides: the {briefing['who_decides']['role']}. {briefing['who_decides']['about']}",
        "Word limits: " + ", ".join(f"{k} {v} words" for k, v in briefing["word_limits"].items())]
    return "\n\n".join(parts)


def task(event: dict) -> str:
    return (f"Assess event {event['id']} from the feed: \"{event['headline']}\" "
            f"(type {event['type']}, about {event['about']['kind']} {event['about']['id']}, "
            f"severity {event['severity']}, verified: {event['verified']}). "
            "Decide whether it is material to Halden and, if so, map the exposure. File your assessment.")


class Bench:
    """What the monitor works from for one event."""

    def __init__(self, connector, briefing: dict, event_id: str):
        self.connector, self.briefing = connector, briefing
        self.event = connector.feed.event(event_id)
        self.traced_revenue: set[int] = {0}     # revenue figures a trace returned this run
        self.traced_products: set[str] = set()   # products a trace returned this run
        self.traced_parts: set[str] = set()      # parts a trace returned this run
        self.traced = False
        self.corroborated = False                 # a second verified event about the same thing was seen
        self.note = None

    def _call(self, operation: str, **given):
        return self.connector.call(MONITOR, operation, **given)

    def tools(self) -> list[Tool]:
        text = {"type": "string"}
        ident = {"type": "string"}

        def read_event(_):
            return self._call("read_event", event=self.event["id"])

        def search_events(given):
            found = self._call("search_events", **{k: given[k] for k in
                               ("type", "kind", "about", "verified", "limit") if k in given})
            if any(e["verified"] and e["id"] != self.event["id"]
                   and e["about"] == self.event["about"] for e in found):
                self.corroborated = True
            return found

        def read_supplier(given):
            return self._call("read_supplier", supplier=given["supplier"])

        def read_part(given):
            return self._call("read_part", part=given["part"])

        def trace_exposure(given):
            out = self._call("trace_exposure", kind=given["kind"], id=given["id"])
            self.traced = True
            self.traced_revenue.add(out["revenue_at_risk_eur"])
            self.traced_products |= {p["id"] for p in out["affected_products"]}
            self.traced_parts |= {p["id"] for p in out["affected_parts"]}
            return out

        def read_cases(_):
            return self._call("read_cases", about=self.event["about"]["id"])

        return [
            Tool("read_event", "The event as the risk feed shows it: source, date, what it is about, severity, "
                 "whether it is verified, and the text.", read_event),
            Tool("search_events", "Other events on the feed, to corroborate or to rule out. Filter by type, by the "
                 "kind of thing (supplier, part, region), by an id, or by verified true/false.", search_events,
                 {"type": text, "kind": text, "about": ident, "verified": {"type": "boolean"},
                  "limit": {"type": "integer"}}, required=[]),
            Tool("read_supplier", "A supplier as the ERP shows it: region, financial health, the parts it supplies, "
                 "its lead time.", read_supplier, {"supplier": ident}, required=["supplier"]),
            Tool("read_part", "A part as the ERP shows it: its family, primary supplier, whether it is single-source, "
                 "on-hand stock and days of cover.", read_part, {"part": ident}, required=["part"]),
            Tool("trace_exposure", "The bill-of-materials walk: from a part, a supplier or a region to the affected "
                 "parts, the products that use them, the open customer orders and the revenue at risk, with the least "
                 "days of cover. 'kind' is one of part, supplier, region; 'id' is its identifier.",
                 trace_exposure, {"kind": text, "id": ident}, required=["kind", "id"]),
            Tool("read_cases", "Earlier assessments that share a supplier, a part or a region with this event, and "
                 "what each one taught.", read_cases),
            Tool("file_exposure", "Hand in the assessment. 'material' is yes or no. If yes, 'kind' is one of "
                 "stoppage, cost, delay, watch. 'affected_products' lists the product ids at risk. "
                 "'revenue_at_risk_eur' is a figure a trace returned. 'min_days_of_cover' is the least cover. "
                 "'confidence' is high, medium or low. 'assessment' says what the event touches and why. 'lesson' is "
                 "one sentence for the next event.", self.file,
                 {"material": {"type": "string", "enum": ["yes", "no"]},
                  "kind": {"type": "string", "enum": list(KINDS)},
                  "affected_products": {"type": "array", "items": ident},
                  "revenue_at_risk_eur": {"type": "integer"}, "min_days_of_cover": {"type": "integer"},
                  "confidence": {"type": "string", "enum": list(CONFIDENCE)},
                  "assessment": text, "lesson": text},
                 required=["material", "kind", "confidence", "assessment", "lesson"], hand_in=True)]

    def file(self, given: dict) -> dict:
        problems = []
        material = str(given.get("material", "")).strip().lower()
        kind = str(given.get("kind", "")).strip().lower()
        confidence = str(given.get("confidence", "")).strip().lower()
        assessment = str(given.get("assessment", "")).strip()
        lesson = str(given.get("lesson", "")).strip()
        products = [str(p).strip() for p in given.get("affected_products") or []]
        revenue = given.get("revenue_at_risk_eur")
        if material not in ("yes", "no"):
            problems.append("'material' must be yes or no.")
        if confidence not in CONFIDENCE:
            problems.append(f"'confidence' must be one of: {', '.join(CONFIDENCE)}.")
        if material == "yes":
            if kind not in ("stoppage", "cost", "delay", "watch"):
                problems.append("For a material event, 'kind' is one of stoppage, cost, delay, watch.")
            if not self.traced:
                problems.append("Run trace_exposure before filing a material exposure: a figure must come from a tool.")
            if revenue is not None and revenue not in self.traced_revenue:
                problems.append(f"EUR {revenue} is not a figure any trace returned in this run. "
                                "Report only the revenue a trace gave you.")
            unseen = sorted(set(products) - self.traced_products)
            if unseen:
                problems.append(f"No trace returned the product(s) {', '.join(unseen)} in this run.")
            if not products:
                problems.append("A material exposure names at least one affected product that a trace returned.")
            if not self.event["verified"] and not self.corroborated:
                problems.append("This event is not verified. A rumour is not an event: call it material only after "
                                "search_events returns a second, verified event about the same thing, or answer 'no'.")
        else:
            kind = "not_material"
        if not assessment:
            problems.append("Say in 'assessment' what the event touches and why.")
        if not lesson:
            problems.append("Say in 'lesson' what this case teaches for the next one.")
        problems += checks.too_long(self.briefing["word_limits"], assessment=assessment, lesson=lesson)
        if problems:
            raise ToolProblem("Not accepted. " + " ".join(problems))
        self.note = {"event": self.event["id"], "headline": self.event["headline"], "material": material == "yes",
                     "kind": kind, "affected_parts": sorted(self.traced_parts), "affected_products": products,
                     "revenue_at_risk_eur": revenue if material == "yes" else 0,
                     "min_days_of_cover": given.get("min_days_of_cover"), "confidence": confidence,
                     "assessment": assessment, "lesson": lesson, "verified_event": self.event["verified"]}
        return self.note
