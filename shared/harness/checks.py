"""Hand-in checks: fixed code that reads what an agent hands in before it is accepted.

No agent can talk its way round these. A hand-in that fails is handed back with
the reasons, and the model corrects it.
"""
import re


def too_long(limits: dict, **texts: str) -> list[str]:
    """One sentence per text that is over the word limit the company briefing sets."""
    return [f"'{k}' has {len(t.split())} words; the limit is {limits[k]}. Shorten it."
            for k, t in texts.items() if k in limits and len((t or "").split()) > limits[k]]


def foreign_amounts(known: set[int], *texts: str) -> list[str]:
    """Euro figures in an agent's text that are not among the amounts a tool produced."""
    foreign = []
    for found in re.findall(r"(?:EUR|\u20ac)\s?(\d[\d.,]*)", " ".join(t or "" for t in texts)):
        digits = found.rstrip(".,")
        whole = re.fullmatch(r"\d{1,3}([.,]\d{3})*|\d+", digits)
        if not whole or int(re.sub(r"[.,]", "", digits)) not in known:
            foreign.append(f"EUR {digits}")
    return foreign
