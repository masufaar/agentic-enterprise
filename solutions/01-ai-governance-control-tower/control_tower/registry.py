"""Agent registry: one card per identity that may act, loaded from data/agents.json.

The registry is the single source of truth for "which agents exist, who owns
them, who approved them and what they may touch".
"""
import json
from pathlib import Path

from . import DATA

REQUIRED = {
    "id", "name", "solution", "owner", "purpose", "model_class",
    "autonomy", "approval", "use_case_flags", "permissions", "today",
}
AUTONOMY = {"advise", "act_with_approval", "act"}
# What stands behind a card today. An agent is a language model working in a loop;
# a step that is fixed code is listed under the identity it acts with, and is not an agent.
TODAY = {"designed": "Designed", "fixed code": "Fixed code, no model",
         "agent in build": "Agent in build", "agent working": "Agent working"}


class RegistryError(ValueError):
    pass


def load(path: Path | None = None) -> dict[str, dict]:
    """Return {agent_id: card}. Fails loudly on an incomplete or duplicate card."""
    path = path or DATA / "agents.json"
    cards = json.loads(path.read_text(encoding="utf-8"))["agents"]
    registry: dict[str, dict] = {}
    for card in cards:
        missing = REQUIRED - card.keys()
        if missing:
            raise RegistryError(f"{card.get('id', '?')}: missing {sorted(missing)}")
        if card["id"] in registry:
            raise RegistryError(f"duplicate agent id {card['id']}")
        if card["autonomy"] not in AUTONOMY:
            raise RegistryError(f"{card['id']}: unknown autonomy {card['autonomy']}")
        if card["today"] not in TODAY:
            raise RegistryError(f"{card['id']}: unknown state today {card['today']}")
        if not card["owner"]:
            raise RegistryError(f"{card['id']}: every agent needs an accountable owner")
        registry[card["id"]] = card
    return registry
