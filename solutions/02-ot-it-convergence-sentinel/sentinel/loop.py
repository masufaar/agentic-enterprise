"""The agent loop: a language model working in a loop inside a harness.

One agent, one job. The loop is the same for every agent:

  1. The model reads its briefing and its task.
  2. It asks for tools. The harness runs each one and hands back the result.
     A tool that cannot do what was asked, or a step the Control Tower does not
     allow, is not the end: the model is told why and decides what to do next.
  3. The agent is finished only when it hands in its result through its hand-in
     tool, and the harness accepts it. A result that fails the harness's checks is
     handed back with the reasons, and the model corrects it.

The model never touches anything itself. It can only ask; the tools are fixed code
and every one of them goes through the Control Tower. The loop keeps a record of
every turn: what the model said, what it asked for, what came back.
"""
import json
import time

from . import Refused


class ToolProblem(Exception):
    """A tool could not do what was asked. The agent is told why and can try something else."""


class Tool:
    """Fixed code the model may ask for. 'hand_in' marks the tool that ends the agent's work."""

    def __init__(self, name: str, description: str, run, properties: dict | None = None,
                 required: list[str] | None = None, hand_in: bool = False):
        self.name, self.run, self.hand_in = name, run, hand_in
        self.schema = {"name": name, "description": description,
                       "input_schema": {"type": "object", "properties": properties or {},
                                        "required": required if required is not None else list(properties or {})}}


def run_agent(name: str, model, system: str, task: str, tools: list[Tool], max_turns: int = 12) -> dict:
    """Run one agent to its hand-in. Returns its result, how it ended and the full record."""
    by_name = {tool.name: tool for tool in tools}
    hand_in = next(tool.name for tool in tools if tool.hand_in)
    turns = [{"role": "user", "text": task}]
    steps, usage, result, ended = [], {"input": 0, "output": 0}, None, "out of turns"
    started = time.monotonic()
    for turn in range(1, max_turns + 1):
        reply = model.ask(system, turns, [tool.schema for tool in tools])
        usage = {k: usage[k] + reply["usage"][k] for k in usage}
        turns.append({"role": "assistant", "text": reply["text"],
                      "tool_calls": reply["tool_calls"], "opaque": reply["opaque"]})
        step = {"turn": turn, "said": reply["text"], "asked": []}
        steps.append(step)
        if reply["stop"] in ("limit", "refused"):
            ended = "cut off" if reply["stop"] == "limit" else "refused by the model"
            break
        if not reply["tool_calls"]:  # it stopped talking without handing in: say so, once more round the loop
            step["reminded"] = True
            turns.append({"role": "user", "text": f"You have not handed in your result. Use the tool {hand_in}."})
            continue
        results = []
        for call in reply["tool_calls"]:
            tool = by_name.get(call["name"])
            try:
                if tool is None:
                    raise ToolProblem(f"There is no tool called {call['name']}.")
                out, failed = tool.run(call["input"]), False
            except (ToolProblem, Refused) as problem:
                out, failed = str(problem), True
            except (KeyError, TypeError, ValueError) as problem:
                out, failed = f"The input could not be used: {problem!r}", True
            step["asked"].append({"tool": call["name"], "input": call["input"], "result": out, "failed": failed})
            results.append({"id": call["id"], "is_error": failed,
                            "content": out if isinstance(out, str) else json.dumps(out)})
            if tool is not None and tool.hand_in and not failed:
                result = out
        turns.append({"role": "tool", "results": results})
        if result is not None:
            ended = "handed in"
            break
    return {"agent": name, "model": model.name, "ended": ended, "result": result, "turns": len(steps),
            "tokens": usage, "seconds": round(time.monotonic() - started, 2), "steps": steps}
