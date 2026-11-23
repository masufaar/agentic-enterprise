"""The analyst agent: what it is told, which tools it may ask for, and what the
harness checks before it accepts the note it hands in.

One agent, one job: challenge each benefit claim as an auditor would, say what is
missing, and write the page the Chief AI Officer takes to the board. It decides
nothing, it changes no budget and it does not do the arithmetic: every figure comes
from the ledger, which is fixed code.

The controls live here, in fixed code, and the agent cannot talk its way round them:
  - every tool call goes through the Control Tower under the agent's own identity;
  - every agent in the ledger needs a verdict, and no other agent may be given one;
  - an agent whose benefit is only claimed cannot be recommended for funding, however
    large the claim: the recommendation is to build the evidence, or to stop;
  - an agent that costs more than it returns on the ledger's own figures cannot be
    recommended for funding;
  - an agent whose cost per use is growing faster than its use must be named to the
    board, in the board text itself;
  - every euro figure the agent writes must be one the ledger produced;
  - every text stays within the word limit the company briefing sets.
"""
from harness import checks

from . import ANALYST, act
from .loop import Tool, ToolProblem
from .ledger import amounts

VERDICTS = {"fund": "Keep its budget.",
            "build the evidence": "Keep it running, and measure the benefit before the next budget round.",
            "stop": "Stop it, or stop paying for it in this form."}

ROLE = (
    "You are the value analyst of the AI portfolio. The company runs AI agents and must say, before the board, "
    "what it gets back for what it spends. The cost side is exact: the invoice arrives. The benefit side is "
    "written by the people who asked for the budget, and your job is to test it as an auditor would. "
    "Read the portfolio first, then every cost and every claim. Where a claim has a measurement behind it, say "
    "what was measured and over what period. Where it has only a formula, say which assumption carries the "
    "result and what would have to be true. Where it has neither, say so plainly: it is a claim, not a result, "
    "and no amount of confidence makes it one. "
    "Where a cost grows faster than the use behind it, say it to the board in your own words. "
    "You do not decide and you do not change a budget. You recommend, and the Chief AI Officer decides with the "
    "Chief Financial Officer. Give every agent in the ledger a verdict: fund, build the evidence, or stop. "
    "Never recommend funding an agent whose benefit is only claimed, or one that costs more than it returns. "
    "Every euro figure you write must be one that a tool returned, written in full with a comma between "
    "thousands, for example EUR 120,000. Do not add figures of different grades together. "
    "Finish with submit_note. If it is not accepted, correct it and submit again.")


def system(briefing: dict) -> str:
    """The role, then the company as the briefing describes it."""
    decides, grades = briefing["who_decides"], briefing["evidence_grades"]
    return "\n\n".join([
        ROLE,
        "COMPANY BRIEFING",
        briefing["company"],
        "What matters, in this order:\n" + "\n".join(f"{n}. {t}" for n, t in enumerate(briefing["what_matters_in_this_order"], 1)),
        "What the grades mean:\n" + "\n".join(f"- {k}: {v}" for k, v in grades.items() if not k.startswith("_")),
        f"Who decides: the {decides['role']}. {decides['about']}",
        "How to write: " + briefing["how_to_write"],
        "Word limits for what you hand in: " + ", ".join(f"{k} {v} words" for k, v in briefing["word_limits"].items()
                                                         if not k.startswith("_")),
    ])


class Desk:
    """What the analyst works from: the ledger of one scenario, and the Control Tower registry."""

    def __init__(self, gateway, ledger: dict, briefing: dict, registry: dict | None = None):
        self.gateway, self.ledger, self.briefing = gateway, ledger, briefing
        self.registry = registry or {}
        self.lines = {l["agent"]: l for l in ledger["lines"]}
        self.read: list[str] = []          # what the agent looked at, for the page
        self.known = amounts(ledger)

    # -- what the harness checks ---------------------------------------------
    def too_long(self, **texts: str) -> list[str]:
        return checks.too_long(self.briefing["word_limits"], **texts)

    def foreign_amounts(self, *texts: str) -> list[str]:
        return checks.foreign_amounts(self.known, *texts)

    def flagged(self) -> list[dict]:
        """Lines whose cost per use is growing faster than their use."""
        return [l for l in self.ledger["lines"] if l["trend"] and l["trend"]["cost_grows_faster_than_use"]]

    def _line(self, agent: str) -> dict:
        if agent not in self.lines:
            raise ToolProblem(f"'{agent}' is not in this ledger. The agents are: {sorted(self.lines)}.")
        self.read.append(agent)
        return self.lines[agent]

    # -- the tools -----------------------------------------------------------
    def tools(self) -> list[Tool]:
        text = {"type": "string"}

        def read_portfolio(_):
            act(self.gateway, ANALYST, "registry.read", {"what": "the agents of this ledger"})
            return {"question": self.ledger["question"],
                    "prices": self.ledger["prices"],
                    "first_year_cost_of_these_agents_eur": self.ledger["cost_eur"],
                    "agents": [{"agent": l["agent"], "name": l["name"], "solution": l["solution"],
                                "owner": l["owner"],
                                "what_the_company_says_it_does_today": l["state_in_the_company"],
                                "what_this_repository_has_behind_its_card": (self.registry.get(l["agent"]) or {}).get("today", "not in the registry"),
                                "first_year_cost_eur": l["cost"]["total_first_year_eur"],
                                "cost_basis": l["cost"]["basis"],
                                "claimed_benefit_eur": l["benefit"]["as_claimed_eur"],
                                "evidence_grade": l["benefit"]["grade"],
                                "cost_over_months_available": bool(l["trend"])} for l in self.ledger["lines"]],
                    "totals_by_grade_eur": {g: t["benefit_eur"] for g, t in self.ledger["totals_by_grade"].items()},
                    "note": "Benefits of different grades are never added together. Two different things are "
                            "shown per agent: what the company says the agent does today, and what this "
                            "repository has behind its card. The second is the build state of the blueprint, not "
                            "the company's operations: an agent can be running at the company while the card in "
                            "this repository still says designed."}

        def read_cost(given):
            line = self._line(given["agent"])
            act(self.gateway, ANALYST, "finance.read", {"what": "cost", "agent": line["agent"]})
            return {"agent": line["agent"], **line["cost"], "net_first_year_eur": line["net_first_year_eur"]}

        def read_claim(given):
            line = self._line(given["agent"])
            act(self.gateway, ANALYST, "finance.read", {"what": "benefit claim", "agent": line["agent"]})
            return {"agent": line["agent"], **line["benefit"],
                    "what_this_grade_means": self.briefing["evidence_grades"][line["benefit"]["grade"]]}

        def read_trend(given):
            line = self._line(given["agent"])
            act(self.gateway, ANALYST, "finance.read", {"what": "cost per use over months", "agent": line["agent"]})
            if not line["trend"]:
                raise ToolProblem(f"No month-by-month cost is recorded for {line['agent']}.")
            return {"agent": line["agent"], **line["trend"]}

        return [
            Tool("read_portfolio", "The agents in this ledger: what each costs in its first year, what is claimed "
                 "for it, the grade of that claim, and what the Control Tower registry says each one is today.",
                 read_portfolio),
            Tool("read_cost", "The cost side of one agent: tokens and euro per unit of work ('unit': a run, or for "
                 "the service desk a verified resolution), units a year, build effort, and whether the cost is "
                 "measured from run records or assumed.", read_cost, {"agent": text}),
            Tool("read_claim", "The benefit claimed for one agent: the figure, who stated it, the grade the ledger "
                 "worked out and why it has that grade.", read_claim, {"agent": text}),
            Tool("read_trend", "Cost per run month by month against the number of runs, for an agent that has "
                 "months recorded.", read_trend, {"agent": text}),
            Tool("submit_note", "Hand in the note for the Chief AI Officer. 'verdicts' is one entry per agent in "
                 "the ledger: agent, verdict (fund, build the evidence, stop) and a short reason. 'for_the_board' "
                 "is what the board is told. 'what_to_measure_first' names the measurement that would change the "
                 "most. 'what_nobody_knows' says what none of this answers.", self.submit,
                 {"verdicts": {"type": "array", "items": {"type": "object", "properties": {
                     "agent": text, "verdict": {"type": "string", "enum": sorted(VERDICTS)}, "reason": text},
                     "required": ["agent", "verdict", "reason"]}},
                  "for_the_board": text, "what_to_measure_first": text, "what_nobody_knows": text},
                 required=["verdicts", "for_the_board", "what_to_measure_first"], hand_in=True)]

    # -- the hand-in ---------------------------------------------------------
    def submit(self, given: dict) -> dict:
        problems, verdicts, seen = [], [], []
        for entry in given.get("verdicts") or []:
            agent = str(entry.get("agent", "")).strip()
            verdict = str(entry.get("verdict", "")).strip()
            reason = str(entry.get("reason", "")).strip()
            if agent not in self.lines:
                problems.append(f"'{agent}' is not an agent in this ledger.")
                continue
            if agent in seen:
                problems.append(f"{agent} has more than one verdict.")
                continue
            seen.append(agent)
            if verdict not in VERDICTS:
                problems.append(f"{agent}: '{verdict}' is not a verdict. Use one of: {', '.join(sorted(VERDICTS))}.")
                continue
            line = self.lines[agent]
            if verdict == "fund" and line["benefit"]["grade"] == "claimed":
                problems.append(f"{agent}: its benefit is only claimed, so it cannot be recommended for funding. "
                                "Recommend building the evidence, or stopping.")
            if verdict == "fund" and line["net_first_year_eur"] <= 0:
                problems.append(f"{agent}: on the ledger's own figures it costs more than it returns, "
                                "so it cannot be recommended for funding.")
            if not reason:
                problems.append(f"{agent}: give a reason.")
            problems += self.too_long(reason=reason)
            verdicts.append({"agent": agent, "verdict": verdict, "reason": reason,
                             "grade": line["benefit"]["grade"]})
        missing = [a for a in self.lines if a not in seen]
        if missing:
            problems.append(f"Every agent in the ledger needs a verdict. Missing: {', '.join(missing)}.")
        board = str(given.get("for_the_board", "")).strip()
        measure = str(given.get("what_to_measure_first", "")).strip()
        unknown = str(given.get("what_nobody_knows", "")).strip()
        if not board:
            problems.append("Write what the board is told in 'for_the_board'.")
        if not measure:
            problems.append("Name the measurement that would change the most in 'what_to_measure_first'.")
        for line in self.flagged():
            words = line["name"].lower().split()
            if not any(w in board.lower() for w in (line["agent"].lower(), " ".join(words[:2]))):
                problems.append(f"The cost per use of {line['agent']} is growing faster than its use. "
                                "The board is told about that agent by name in 'for_the_board'.")
        problems += self.too_long(for_the_board=board, what_to_measure_first=measure, what_nobody_knows=unknown)
        foreign = self.foreign_amounts(board, measure, unknown, *[v["reason"] for v in verdicts])
        if foreign:
            problems.append(f"These figures did not come from a tool: {', '.join(foreign)}. "
                            "Use only the ledger's figures, written in full.")
        if problems:
            raise ToolProblem("Not accepted. " + " ".join(problems))
        return {"verdicts": verdicts, "for_the_board": board, "what_to_measure_first": measure,
                "what_nobody_knows": unknown}
