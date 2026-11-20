"""The page for the Chief AI Officer: one page, and what is behind every figure.

The page is put together by fixed code. The analyst's words appear as its words, in
quotation. Totals are held apart by grade, because a measured euro and a claimed euro
are not the same money, and the page says on every line where its figures come from.
"""
from datetime import date

from harness.page import agent_turns, quote, tokens

from . import cents, eur

GRADE_WORDS = {"measured": "measured", "calculated": "calculated from assumptions", "claimed": "claimed only"}


def _line_row(line: dict) -> str:
    cost, benefit = line["cost"], line["benefit"]
    return (f"| {line['name']} | {eur(cost['total_first_year_eur'])} ({cost['basis']}) | "
            f"{eur(benefit['value_eur'])} ({GRADE_WORDS[benefit['grade']]}) | {line['owner']} |")


def page(result: dict) -> str:
    """The whole page, as markdown."""
    ledger, note = result["ledger"], result["note"]
    verdict_of = {v["agent"]: v for v in (note or {}).get("verdicts", [])}
    out = [f"# AI Value Ledger: {ledger['title']}", "",
           f"For the {result['decides']}, with the Chief Financial Officer. "
           f"Prepared {date.today().isoformat()}. All data is synthetic (Halden Industrial), "
           f"except the cost of agents marked measured, which is read from the run records in this repository.", ""]
    if ledger["question"]:
        out += [f"**The question:** {ledger['question']}", ""]
    out += ["## The ledger", "",
            "| Agent | First-year cost | Benefit | Owner |", "|---|---|---|---|"]
    out += [_line_row(l) for l in ledger["lines"]]
    out += ["", f"First-year cost of these agents: {eur(ledger['cost_eur'])}, "
                f"of which {eur(ledger['cost_measured_eur'])} is measured from run records.", "",
            "Benefit, held apart by the evidence behind it, never added together:", ""]
    for grade, total in ledger["totals_by_grade"].items():
        if total["agents"]:
            out.append(f"- **{GRADE_WORDS[grade].capitalize()}:** {eur(total['benefit_eur'])} "
                       f"({', '.join(total['agents'])})")
    out += ["", "## What the analyst recommends", ""]
    if not note and not result["runs"]:
        out += ["No agent ran: this page is the ledger alone, which is fixed code.", ""]
    elif not note:
        out += ["The analyst agent did not hand in a note that the harness accepted. "
                "The ledger above is fixed code and stands on its own.", ""]
    else:
        out += ["| Agent | Recommendation | Why |", "|---|---|---|"]
        for line in ledger["lines"]:
            v = verdict_of.get(line["agent"], {})
            out.append(f"| {line['name']} | {v.get('verdict', '-')} | {v.get('reason', '-')} |")
        out += ["", "**For the board, in the analyst's words:**", ""] + quote(note["for_the_board"])
        out += ["", "**What to measure first:**", ""] + quote(note["what_to_measure_first"])
        if note.get("what_nobody_knows"):
            out += ["", "**What nobody knows:**", ""] + quote(note["what_nobody_knows"])
    out += ["", "## Behind every figure", ""]
    for line in ledger["lines"]:
        cost, benefit = line["cost"], line["benefit"]
        out += [f"**{line['name']}** ({line['agent']})", "",
                f"- Cost, {cost['basis']}: {cents(cost['eur_per_run'])} a run on {cost['model']}, "
                f"{cost['runs_per_year']:,} runs a year ({cost['runs_per_year_basis']}), "
                f"build {cost['build_hours']} hours at {eur(result['build_hour_eur'])} an hour, "
                f"= {eur(cost['total_first_year_eur'])} in the first year.",
                f"- {cost['evidence']['note']}"]
        if cost["evidence"]["files"]:
            out.append(f"- Run records read: {', '.join(cost['evidence']['files'])}.")
        out += [f"- Benefit {eur(benefit['value_eur'])}, stated by the {benefit['stated_by']}. "
                f"Grade: {GRADE_WORDS[benefit['grade']]}. {benefit['why']}"]
        if benefit["source"]:
            out.append(f"- Source of the claim: {benefit['source']}.")
        if line["trend"]:
            t = line["trend"]
            out.append(f"- Cost per use, {t['first']} to {t['last']}: use {t['use_change_pct']:+.1f}%, "
                       f"cost per run {t['cost_per_run_change_pct']:+.1f}%."
                       + (" Cost is growing faster than use." if t["cost_grows_faster_than_use"] else ""))
        out.append("")
    out += ["## How this page was made", "",
            f"- Prices: {ledger['prices']['source']}; euro at {ledger['prices']['eur_per_usd']} per USD (assumption).",
            f"- The analyst agent is registered in the Control Tower as advising only; "
            f"the {result.get('answers_for_the_agent', 'owner')} answers for it.",
            f"- The ledger is fixed code. The analyst agent ({result['analyst']}) read: "
            f"{', '.join(sorted(set(result['read']))) or 'nothing'}.",
            agent_turns(result["runs"]) if result["runs"] else "- No agent ran.",
            f"- {tokens(result['tokens'])} Seconds to this page: {result['seconds_to_page']}.",
            "- Every step of the agent passed the AI Governance Control Tower under its own identity.", ""]
    return "\n".join(out)
