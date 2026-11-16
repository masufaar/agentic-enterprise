"""Kill switch: stop one agent or all agents. Checked before anything else."""
import json
from pathlib import Path

from . import STATE


class KillSwitch:
    def __init__(self, path: Path | None = None):
        self.path = path or STATE / "killswitch.json"

    def _read(self) -> dict:
        if self.path.exists():
            return json.loads(self.path.read_text())
        return {"all": False, "agents": []}

    def _write(self, state: dict) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(state, indent=2))

    def kill(self, agent_id: str = "all") -> None:
        state = self._read()
        if agent_id == "all":
            state["all"] = True
        elif agent_id not in state["agents"]:
            state["agents"].append(agent_id)
        self._write(state)

    def revive(self, agent_id: str = "all") -> None:
        state = self._read()
        if agent_id == "all":
            state = {"all": False, "agents": []}
        else:
            state["agents"] = [a for a in state["agents"] if a != agent_id]
        self._write(state)

    def is_killed(self, agent_id: str) -> bool:
        state = self._read()
        return state["all"] or agent_id in state["agents"]

    def stopped(self) -> list[str]:
        """Who is switched off right now: ["all"] or a list of agent ids."""
        state = self._read()
        return ["all"] if state["all"] else list(state["agents"])
