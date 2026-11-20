"""The shared agent harness: what every solution's agents run in.

An agent is a language model working in a loop inside a harness. This package is
that harness, taken out of solution 02 so that every solution uses the same one:

  loop.py    the agent loop: the model asks for tools, fixed code runs them, and the
             agent is finished only when its hand-in is accepted
  model.py   the model connector: one neutral format, a scripted stand-in for the
             tests, and a connector for Claude
  hooks.py   the one door to the Control Tower: every tool call is announced there
             and comes back as allow, deny or ask
  checks.py  the hand-in checks: word limits, and figures that must come from a tool
  cases.py   the case memory: one file per case, written through the Control Tower
  page.py    the frame of a decision page: agents' words in quotation, and how the
             page was made

Standard library only. The harness does not import the Control Tower: a solution
hands it a gateway, and anything with the same 'execute' can stand in its place.
"""
from .hooks import Refused, act, tool_call_request

__all__ = ["Refused", "act", "tool_call_request"]
