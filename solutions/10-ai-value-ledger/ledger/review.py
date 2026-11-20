"""One review, from the ledger to the page.

  1. The ledger is built in fixed code: costs from run records or from the portfolio
     file, benefits graded by the evidence that exists.
  2. The analyst agent reads it, challenges every claim and hands in its note. The
     harness checks the note before it accepts it.
  3. The page for the Chief AI Officer is written, with the analyst's words in
     quotation and the source of every figure under it.

Nothing here changes a budget. The ledger reads; the agent recommends; a named
person decides.
"""
import json
import time

from control_tower.audit import AuditLog
from control_tower.gateway import Gateway
from control_tower.killswitch import KillSwitch

from . import ANALYST, DATA, load
from . import analyst as analyst_module
from . import board, ledger as ledger_module
from .loop import run_agent

DEFAULT_SCENARIO = "pays-back"


def gateway(audit: AuditLog | None = None, killswitch: KillSwitch | None = None) -> Gateway:
    """The Control Tower gateway. The analyst is a card in the Tower's registry."""
    return Gateway(audit=audit, killswitch=killswitch)


def load_scenario(name: str = DEFAULT_SCENARIO) -> dict:
    return json.loads((DATA / "scenarios" / f"{name}.json").read_text(encoding="utf-8"))


def task(ledger: dict) -> str:
    agents = ", ".join(l["agent"] for l in ledger["lines"])
    return (f"The ledger for this review holds these agents: {agents}. {ledger['question']} "
            "Read the portfolio, then every cost and every claim, and hand in your note.")


def run_review(model, gate: Gateway | None = None, scenario: str = DEFAULT_SCENARIO,
               briefing: dict | None = None) -> dict:
    """Build the ledger, run the analyst on it and write the page."""
    gate = gate if gate is not None else gateway()
    briefing = briefing if briefing is not None else load("briefing.json")
    card = gate.registry[ANALYST]
    if card["autonomy"] != "advise":
        raise ValueError(f"The Control Tower registry gives {ANALYST} the autonomy '{card['autonomy']}'. "
                         "This agent recommends and explains; it decides nothing and changes no budget, so it "
                         "runs only while its card says 'advise'.")
    owner, decides = card["owner"], briefing["who_decides"]["role"]
    started = time.monotonic()
    chosen = load_scenario(scenario)
    built = ledger_module.build(chosen)
    desk = analyst_module.Desk(gate, built, briefing, registry=gate.registry)
    run = run_agent(ANALYST, model, analyst_module.system(briefing), task(built), desk.tools())
    result = {"scenario": scenario, "ledger": built, "note": run["result"], "decides": decides,
              "answers_for_the_agent": owner,
              "analyst": run["model"], "runs": [run], "read": desk.read,
              "build_hour_eur": built["build_hour_eur"],
              "tokens": dict(run["tokens"]), "seconds_to_page": round(time.monotonic() - started, 2),
              "flagged": [l["agent"] for l in desk.flagged()]}
    result["page"] = board.page(result)
    act_report(gate, result)
    return result


def act_report(gate: Gateway, result: dict) -> None:
    """Writing the page is itself a step of the agent's identity, and goes through the Tower."""
    from . import act
    act(gate, ANALYST, "report.write", {"report": f"value ledger, {result['scenario']}",
                                        "characters": len(result["page"])})
