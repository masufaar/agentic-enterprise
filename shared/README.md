# Shared agent harness

**Status: Working as a blueprint (20 November 2026). No model of its own: it is what every solution's agents run in. ACS wire format and conformance test: designed.**

An agent is a language model working in a loop inside a harness. This folder is that harness, one for every solution, taken out of solution 02 so that the next solutions do not each build their own.

| Part | What it does |
|---|---|
| `harness/loop.py` | The agent loop. The model asks for tools; fixed code runs them; a failed or refused step is handed back to the model; the agent is finished only when its hand-in is accepted. |
| `harness/model.py` | The model connector. One neutral format, a scripted stand-in for the tests, and a connector for Claude. A company enters its own model here. |
| `harness/hooks.py` | The one door to the Control Tower. Every tool call is announced and comes back as `allow`, `deny` or `ask` (held for a named person). Shaped like the tool-call request hook of the OWASP Agent Control Standard, v0.1.0. |
| `harness/checks.py` | Hand-in checks: word limits, and euro figures that must come from a tool. |
| `harness/cases.py` | The case book: one file per case, written through the Control Tower. |
| `harness/page.py` | The frame of a decision page: agents' words in quotation, and how the page was made. |

What is not built: the hook runs in process and calls the gateway directly. The standard's JSON-RPC wire format, its signature on every message, the tool-call result hook and the conformance test are designed. Until the conformance test has run and its result is published, nothing here is called conformant.

Tests: `cd shared; python -m pytest` (15 tests, against the real gateway of solution 01, no model and no key). Solution 02 runs on this harness and passes its 92 tests unchanged.

Key file for real runs: the environment variable `HALDEN_MODEL_KEY_FILE`; solution 02's first name, `SENTINEL_MODEL_KEY_FILE`, still works.
