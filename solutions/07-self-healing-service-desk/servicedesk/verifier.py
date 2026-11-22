"""The verifier agent: it reopens the question on a ticket that is already closed.

One agent, one job, one closed ticket at a time: did the fix hold, was the
requester entitled, does the record match what was done. It checks tickets closed
by our resolution agent, by the suite's own agent and by people, the same way.

It never closes or changes a ticket. That is not an instruction it could be talked
out of: it is given no tool that changes one, its registry card holds none, and the
Control Tower refuses it on every ticket type.

The controls live here, in fixed code:
  - every tool call goes through the connector and the Control Tower under the
    verifier's own identity;
  - a finding is accepted only after the owner's record, the suite's action log and
    the later tickets have each been read in this run;
  - 'the fix did not hold' must name a later ticket that a tool returned in this run;
    every ticket named as evidence must be one a tool returned;
  - 'the fix held' is not accepted before the follow-up days in the briefing are over:
    the honest answer until then is 'cannot tell';
  - a 'no' needs the reason in words; every text stays within the briefing's limits;
  - what a finding means for the autonomy ladder is worked out by fixed code.
"""
import re
from datetime import datetime, timedelta

from harness import checks
from harness.loop import Tool, ToolProblem

from . import VERIFIER
from .findings import ANSWERS, QUESTIONS

ROLE = (
    "You are the verifier of the IT service desk. You are given one ticket that is already closed, by an AI agent "
    "or by a person. You do not trust the word 'closed'. You answer three questions from evidence: did the fix "
    "hold, was the requester entitled to ask, and does the note on the ticket match what the action log shows was "
    "done. Read the ticket, then the owner's record, the action log and the tickets that came later, and the "
    "earlier cases if any. A later ticket from the same person about the same thing means the fix did not hold, "
    "even when it is worded differently and nothing links the two; a later ticket about something else does not. "
    "Answer each question yes, no or cannot tell. 'Cannot tell' is a good answer when the evidence is not there "
    "yet; a guess is not. You never close, reopen or change a ticket, and you have no tool for it. Say in one "
    "sentence what this case teaches for the next one. Finish with file_finding. If it is not accepted, correct "
    "it and file again.")


def system(briefing: dict) -> str:
    """The role, then the company as the briefing in force describes it."""
    looks, rules = briefing["what_a_check_looks_at"], briefing["entitlement"]
    parts = [
        ROLE, "COMPANY BRIEFING", briefing["company"],
        "What matters, in this order:\n" + "\n".join(f"{n}. {t}" for n, t in enumerate(briefing["what_matters_in_this_order"], 1)),
        "What each question looks at:\n" + "\n".join(f"- {k}: {v}" for k, v in looks.items()),
        "Who may ask for what:\n" + "\n".join(f"- {k}: {v}" for k, v in rules.items() if isinstance(v, str) and not k.startswith("_")),
        f"Confirmations that count: {', '.join(rules['confirmations_that_count'])}.",
        f"Who decides: the {briefing['who_decides']['role']}. {briefing['who_decides']['about']}",
        "How to write: " + briefing["how_to_write"],
        "Word limits: " + ", ".join(f"{k} {v} words" for k, v in briefing["word_limits"].items())]
    if briefing.get("standing_instructions"):
        parts.append("Standing instructions in force:\n" + "\n".join(
            f"- For {i['applies_to']}: {i['instruction']}" for i in briefing["standing_instructions"]))
    return "\n\n".join(parts)


def task(ticket: dict) -> str:
    return (f"Check the closed ticket {ticket['id']} (type {ticket['type']}, closed by {ticket['closed_by']} "
            f"on {ticket['closed_at']}). Read the evidence and file your finding.")


class Bench:
    """What the verifier works from for one closed ticket."""

    def __init__(self, connector, findings, memory, briefing: dict, ticket_id: str):
        self.connector, self.findings, self.memory, self.briefing = connector, findings, memory, briefing
        self.ticket = connector.suite.ticket(ticket_id)
        if self.ticket["state"] != "closed":
            raise ValueError(f"{ticket_id} is {self.ticket['state']}. The verifier checks closed tickets only.")
        self.read: set[str] = set()       # which sources were read in this run
        self.seen: set[str] = {ticket_id}  # every ticket a tool returned in this run
        self.later: set[str] = set()
        self.finding = None

    def _call(self, operation: str, **given):
        return self.connector.call(VERIFIER, operation, ticket=self.ticket["id"], **given)

    def tools(self) -> list[Tool]:
        text = {"type": "string"}
        answer = {"type": "string", "enum": list(ANSWERS)}

        def read_ticket(_):
            return self._call("get_ticket")

        def look_up_owner(_):
            self.read.add("the owner's record")
            return self._call("get_owner")

        def read_action_log(_):
            self.read.add("the action log")
            return self._call("get_action_log")

        def read_later_tickets(_):
            self.read.add("the later tickets")
            found = self._call("get_later_tickets", days=self.briefing["follow_up_days"])
            self.later = {t["id"] for t in found}
            self.seen |= self.later
            return {"days": self.briefing["follow_up_days"], "later_tickets": found,
                    "note": "From the same requester, or about the same thing. Nothing links them to this ticket; "
                            "whether one of them is the same problem is for you to judge."}

        def read_cases(_):
            found = self.memory.read(self.connector.gateway, VERIFIER, self.ticket)
            self.seen |= {c["ticket"] for c in found["earlier_cases"]}
            return found

        return [
            Tool("read_ticket", "The closed ticket as the suite shows it: who asked, about what, in which words, "
                 "what was confirmed, who closed it, with which action and which note.", read_ticket),
            Tool("look_up_owner", "Who owns the account, laptop, folder or application the ticket is about, from the "
                 "company's own records.", look_up_owner),
            Tool("read_action_log", "What the suite's log shows was done for this ticket, by whom, and the signals "
                 "that arrived afterwards.", read_action_log),
            Tool("read_later_tickets", "Tickets opened after this one was closed, by the same requester or about the "
                 "same thing, within the follow-up days of the briefing.", read_later_tickets),
            Tool("read_cases", "Earlier cases that share a device, an account, a group of incidents or a site with "
                 "this ticket, and what each one taught.", read_cases),
            Tool("file_finding", "Hand in the finding. Each of fix_held, requester_entitled and record_matches is "
                 "yes, no or cannot tell. 'evidence' lists the ticket numbers the finding rests on. 'finding' says "
                 "what you saw and where. 'lesson' is one sentence for the next case.", self.file,
                 {"fix_held": answer, "requester_entitled": answer, "record_matches": answer,
                  "evidence": {"type": "array", "items": text}, "finding": text, "lesson": text},
                 required=["fix_held", "requester_entitled", "record_matches", "finding", "lesson"], hand_in=True)]

    # -- the hand-in -----------------------------------------------------------
    def file(self, given: dict) -> dict:
        problems = []
        answers = {q: str(given.get(q, "")).strip().lower() for q in QUESTIONS}
        for question, value in answers.items():
            if value not in ANSWERS:
                problems.append(f"'{question}' must be one of: {', '.join(ANSWERS)}.")
        unread = [s for s in ("the owner's record", "the action log", "the later tickets") if s not in self.read]
        if unread:
            problems.append(f"You have not read {', '.join(unread)}. A finding rests on all three.")
        words, lesson = str(given.get("finding", "")).strip(), str(given.get("lesson", "")).strip()
        evidence = [str(e).strip() for e in given.get("evidence") or []]
        named = set(evidence) | set(re.findall(r"SD-\d\d-\d{4}", f"{words} {lesson}"))
        unseen = sorted(named - self.seen)
        if unseen:
            problems.append(f"No tool returned {', '.join(unseen)} in this run. Name only tickets you have read.")
        if answers["fix_held"] == "no" and not (set(evidence) & self.later):
            problems.append("'The fix did not hold' must name, in 'evidence', a later ticket that read_later_tickets returned.")
        over = datetime.fromisoformat(self.ticket["closed_at"]) + timedelta(days=self.briefing["follow_up_days"])
        if answers["fix_held"] == "yes" and datetime.fromisoformat(self.connector.suite.as_of) < over:
            problems.append(f"It is too early to say the fix held: the ticket was closed on {self.ticket['closed_at']} "
                            f"and the {self.briefing['follow_up_days']} follow-up days are not over. Answer 'cannot tell'.")
        if "no" in answers.values() and not words:
            problems.append("A 'no' needs the reason in 'finding': what you saw and where.")
        if not lesson:
            problems.append("Say in 'lesson' what this case teaches for the next one.")
        problems += checks.too_long(self.briefing["word_limits"], finding=words, lesson=lesson)
        if problems:
            raise ToolProblem("Not accepted. " + " ".join(problems))
        self.finding = self.findings.write(self.ticket, answers, evidence, words)
        self.memory.keep(self.connector.gateway, VERIFIER, "checked", self.ticket, answers=answers,
                         outcome=self.finding["outcome"], words=words, lesson=lesson)
        return {**self.finding, "lesson": lesson}
