"""The frame of a decision page.

A page is put together by fixed code. The agents' words appear on it as theirs,
in quotation, and the page says how it was made: which agents ran, how they ended,
how long it took and what it cost in tokens. What stands between is each solution's own.
"""


def quote(text: str) -> list[str]:
    """An agent's words, shown as a quotation."""
    return [f"> {line}" for line in (text or "").splitlines() if line.strip()] or ["> (nothing written)"]


def agent_turns(runs: list[dict]) -> str:
    return "- Agent turns: " + ", ".join(f"{r['agent']} {r['turns']} ({r['ended']})" for r in runs) + "."


def tokens(usage: dict) -> str:
    return f"Tokens: {usage['input']:,} in, {usage['output']:,} out."
