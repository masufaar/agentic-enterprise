"""The three agents of a night: what each is told, which tools it may ask for, and
what the harness checks before it accepts a result.

  first response   takes the few office-side steps that can be undone in minutes
  planner          prices responses and recommends one for the plant floor
  challenger       argues against the planner's recommendation

Each is a language model in the loop of sentinel/loop.py. What they are told about
the company comes from data/briefing.json, not from this file.

Three controls live here, in fixed code, and no agent can talk its way round them:
  - every tool goes through the Control Tower under the agent's own identity;
  - every euro figure an agent writes must be one the pricing tool produced;
  - a first-response step is taken only if the briefing allows it, on the office
    side, against a device or account that is part of the incident.
"""
import re

from . import act
from .loop import Tool, ToolProblem
from .response import price

FIRST, PLANNER, CHALLENGER = "ot-first-response", "ot-response", "ot-challenger"
STEP_TOOLS = {"suspend_account": "identity.account.suspend",
              "quarantine_workstation": "endpoint.quarantine",
              "close_remote_session": "remote_access.session.close"}

ROLES = {
    FIRST: (
        "You are the first-response agent of the security crisis team. An intrusion is under way. "
        "Your job is narrow: take the steps on the office side that slow the intruder down and can be undone "
        "in minutes. You have no permission on the plant floor and you do not recommend plant-floor steps. "
        "Read the incident and the plant first. Take a step only when the incident gives a reason for it. "
        "If a tool refuses a step, do not try to reach the same effect another way; note it. "
        "Finish with report_first_response, saying what you left alone and why."),
    PLANNER: (
        "You are the planner of the security crisis team. An intrusion is under way and a named person must "
        "decide within minutes what to disconnect on the plant floor. You prepare that decision; you do not take it. "
        "Read the incident, the plant and the production plan. Price every response you consider with "
        "price_response, including combinations, and compare what each costs with what it leaves within the "
        "intruder's reach. Recommend one. If no response closes every path, say so plainly. "
        "Every euro figure you write must be one that price_response returned. "
        "Finish with submit_plan. If it is not accepted, correct it and submit again."),
    CHALLENGER: (
        "You are the challenger of the security crisis team. The planner has recommended a response. Your job is "
        "to find what is wrong with it before a person relies on it: a cheaper response that is as safe, a path it "
        "leaves open, an assumption that carries the result, something nobody knows. Check the planner's figures "
        "with price_response rather than trusting them. Agree only if you looked and found nothing; an empty "
        "objection wastes the decider's time as much as a missed one. "
        "Every euro figure you write must be one that price_response returned. Finish with submit_challenge."),
}


def system(agent: str, briefing: dict) -> str:
    """The role, then the company as the briefing describes it."""
    decides = briefing["who_decides"]
    return "\n\n".join([
        ROLES[agent],
        "COMPANY BRIEFING",
        briefing["company"],
        "What matters, in this order:\n" + "\n".join(f"{n}. {t}" for n, t in enumerate(briefing["what_matters_in_this_order"], 1)),
        f"Who decides: the {decides['role']}. {decides['about']}",
        "How to write: " + briefing["how_to_write"],
    ])


class Desk:
    """What the agents of one night share: the facts, and the list of everything priced or done."""

    def __init__(self, gateway, incident: dict, unrelated: list, plant: dict, production: dict, briefing: dict):
        self.gateway, self.incident, self.unrelated = gateway, incident, unrelated
        self.plant, self.production, self.briefing = plant, production, briefing
        self.priced: dict[str, dict] = {}   # every response priced tonight, by its steps
        self.first_steps: list[dict] = []   # office-side steps actually carried out
        self.steps = {p["id"]: p for p in plant["isolation_points"]}

    # -- pricing -------------------------------------------------------------
    def key(self, steps) -> str:
        if not isinstance(steps, list) or any(s not in self.steps for s in steps):
            unknown = steps if not isinstance(steps, list) else [s for s in steps if s not in self.steps]
            raise ToolProblem(f"Not a response step that is available tonight: {unknown}. "
                              f"Available: {sorted(self.steps)}.")
        return "+".join(s for s in self.steps if s in steps)  # one order, whatever order was asked

    def price(self, steps: list) -> dict:
        key = self.key(steps)
        if key not in self.priced:
            self.priced[key] = price([self.steps[s] for s in self.steps if s in steps],
                                     self.incident, self.plant, self.production)
        return self.priced[key]

    def known_amounts(self) -> set[int]:
        costs = [p["cost_eur"] for p in self.priced.values()]
        known = {self.production["cost_per_stopped_line_hour_eur"]} | set(costs)
        for p in self.priced.values():
            known |= {p["still_at_stake_eur"], p["cost_eur"] + p["still_at_stake_eur"]}
            known |= {line["cost_eur"] for line in p["lines_stopped"]}
        return known | {abs(a - b) for a in costs for b in costs}

    def foreign_amounts(self, *texts: str) -> list[str]:
        """Euro figures in an agent's text that the pricing tool did not produce."""
        foreign = []
        for found in re.findall(r"(?:EUR|€)\s?(\d[\d.,]*)", " ".join(t or "" for t in texts)):
            digits = found.rstrip(".,")
            whole = re.fullmatch(r"\d{1,3}([.,]\d{3})*|\d+", digits)
            if not whole or int(re.sub(r"[.,]", "", digits)) not in self.known_amounts():
                foreign.append(f"EUR {digits}")
        return foreign

    # -- tools every agent may ask for ---------------------------------------
    def reading_tools(self, agent: str, with_pricing: bool = True) -> list[Tool]:
        def read_incident(_):
            act(self.gateway, agent, "incident.read", {"incident": self.incident["id"]})
            return {"incident": self.incident, "alerts_set_aside_as_unrelated": self.unrelated,
                    "office_side_steps_already_taken": self.first_steps}

        def read_plant(_):
            act(self.gateway, agent, "network.read", {"what": "plant layout", "plant": self.plant["plant"]["id"]})
            return {k: self.plant[k] for k in ("plant", "zones", "assets", "connections")} | {
                "response_steps_available": self.plant["isolation_points"],
                "response_steps_not_available_tonight": self.plant.get("unavailable_steps", {})}

        def read_production(_):
            act(self.gateway, agent, "production.read", {"what": "schedule and cost of a stopped line-hour"})
            return {k: v for k, v in self.production.items() if k != "_note"}

        def price_response(given):
            act(self.gateway, agent, "production.read", {"what": "price of a response", "steps": given["steps"]})
            return self.price(given["steps"])

        tools = [Tool("read_incident", "The incident: timeline, devices under the intruder's control, accounts used, "
                      "and the office-side steps already taken.", read_incident),
                 Tool("read_plant", "The plant: zones, devices, connections, and the response steps available tonight.",
                      read_plant)]
        if with_pricing:
            tools += [
                Tool("read_production", "The production plan and the assumptions behind every price.", read_production),
                Tool("price_response", "Price one response: the lost output it causes, line by line, and the lines "
                     "still within the intruder's reach afterwards. 'steps' is a list of response step ids; an empty "
                     "list prices doing nothing.", price_response,
                     {"steps": {"type": "array", "items": {"type": "string"}}})]
        return tools

    # -- the first-response agent --------------------------------------------
    def first_response_tools(self) -> list[Tool]:
        rules = self.briefing["first_response"]
        side_of = {z["id"]: z["side"] for z in self.plant["zones"]}
        zone_of = {a["id"]: a["zone"] for a in self.plant["assets"]}

        def take(step: str, target: str):
            if step not in rules["allowed_steps"]:
                raise ToolProblem(f"The company briefing does not allow the step '{step}' without a person.")
            if any(s["step"] == step and s["target"] == target for s in self.first_steps):
                raise ToolProblem("Already done tonight.")
            if step == "suspend_account":
                if target not in self.incident["accounts"]:
                    raise ToolProblem(f"{target} is not an account used in this incident.")
                if target in rules["never_suspend"]:
                    raise ToolProblem(f"The company briefing says {target} is never suspended without a person.")
            else:
                if target not in self.incident["path"]:
                    raise ToolProblem(f"{target} is not a device on the path of this incident.")
                if side_of.get(zone_of.get(target)) not in rules["allowed_sides"]:
                    raise ToolProblem(f"{target} is on the plant floor. Steps there are decided by the "
                                      f"{self.briefing['who_decides']['role']}, not taken by an agent.")
            verdict = act(self.gateway, FIRST, STEP_TOOLS[step], {"target": target, "incident": self.incident["id"]})
            done = {"step": step, "target": target, "undo": rules["allowed_steps"][step],
                    "audit_record": verdict["audit_seq"]}
            self.first_steps.append(done)
            return done

        def report(given):
            return {"left_alone": str(given["left_alone"]).strip()}

        text = {"type": "string"}
        return self.reading_tools(FIRST, with_pricing=False) + [
            Tool("suspend_account", "Suspend an account used in the incident. Can be undone.",
                 lambda g: take("suspend_account", g["account"]), {"account": text}),
            Tool("quarantine_workstation", "Cut an office-side device of the incident off the network. Can be undone.",
                 lambda g: take("quarantine_workstation", g["device"]), {"device": text}),
            Tool("close_remote_session", "Close the remote sessions on an office-side device of the incident. "
                 "Can be undone.", lambda g: take("close_remote_session", g["device"]), {"device": text}),
            Tool("report_first_response", "Hand in: what you left alone and why. The steps you took are already "
                 "recorded.", report, {"left_alone": text}, hand_in=True)]

    # -- the planner ---------------------------------------------------------
    def planner_tools(self, answering: bool = False) -> list[Tool]:
        limit = self.briefing["debate"]["options_on_the_page"]

        def submit(given):
            problems, keys = [], []
            for steps in [given["recommended"]] + list(given["options"]):
                key = self.key(steps)
                if key not in self.priced:
                    problems.append(f"The response {steps} has not been priced. Price it first.")
                elif key not in keys:
                    keys.append(key)
            if len(keys) < 2:
                problems.append("Give the decider at least two responses to choose from.")
            if len(keys) > limit:
                problems.append(f"At most {limit} responses fit on the page; you gave {len(keys)}.")
            texts = [str(given.get(f, "")).strip() for f in ("why", "what_remains_open", "answer_to_challenger")]
            foreign = self.foreign_amounts(*texts)
            if foreign:
                problems.append(f"These figures did not come from price_response: {', '.join(foreign)}. "
                                "Use only priced figures, written in full.")
            if not texts[0]:
                problems.append("Say why you recommend this response.")
            recommended = self.priced.get(self.key(given["recommended"]))
            closes = bool(recommended) and not recommended["lines_still_reachable"]
            if recommended and not closes and not texts[1]:
                problems.append("Your recommendation leaves lines within the intruder's reach. "
                                "Say so in 'what_remains_open'.")
            if answering and not texts[2]:
                problems.append("Answer the challenger in 'answer_to_challenger'.")
            if problems:
                raise ToolProblem("Not accepted. " + " ".join(problems))
            return {"recommended": self.key(given["recommended"]), "options": keys, "why": texts[0],
                    "what_remains_open": texts[1], "answer_to_challenger": texts[2], "closes_every_path": closes}

        text, steps = {"type": "string"}, {"type": "array", "items": {"type": "string"}}
        return self.reading_tools(PLANNER) + [
            Tool("submit_plan", "Hand in the plan. 'options' are the responses the decider chooses from, each a list "
                 "of step ids, all priced. 'recommended' is one of them. 'what_remains_open' says what the "
                 "recommendation does not cover and what nobody knows.", submit,
                 {"options": {"type": "array", "items": steps}, "recommended": steps, "why": text,
                  "what_remains_open": text, "answer_to_challenger": text},
                 required=["options", "recommended", "why", "what_remains_open"], hand_in=True)]

    # -- the challenger ------------------------------------------------------
    def challenger_tools(self) -> list[Tool]:
        def submit(given):
            problems = []
            if given["verdict"] not in ("agree", "object"):
                problems.append("'verdict' is either agree or object.")
            argument = str(given.get("argument", "")).strip()
            if not argument:
                problems.append("Give your argument, also when you agree: say what you checked.")
            alternative = given.get("alternative")
            if alternative is not None and self.key(alternative) not in self.priced:
                problems.append("Price your alternative first.")
            foreign = self.foreign_amounts(argument, str(given.get("what_nobody_knows", "")))
            if foreign:
                problems.append(f"These figures did not come from price_response: {', '.join(foreign)}.")
            if problems:
                raise ToolProblem("Not accepted. " + " ".join(problems))
            return {"verdict": given["verdict"], "argument": argument,
                    "alternative": self.key(alternative) if alternative is not None else None,
                    "what_nobody_knows": str(given.get("what_nobody_knows", "")).strip()}

        text = {"type": "string"}
        return self.reading_tools(CHALLENGER) + [
            Tool("submit_challenge", "Hand in your verdict on the planner's recommendation: 'agree' or 'object', your "
                 "argument, optionally a priced 'alternative' (list of step ids), and what nobody knows.", submit,
                 {"verdict": {"type": "string", "enum": ["agree", "object"]}, "argument": text,
                  "alternative": {"type": "array", "items": {"type": "string"}}, "what_nobody_knows": text},
                 required=["verdict", "argument"], hand_in=True)]
