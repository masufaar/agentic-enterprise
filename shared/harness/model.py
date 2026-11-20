"""The model connector: the one place where a language model is called.

Every solution speaks one neutral format, so a company can enter its own
model without touching the agents:

  ask(system, turns, tools) -> reply

  turns   a list of {"role": "user", "text": ...}
                    {"role": "assistant", "text": ..., "tool_calls": [...], "opaque": ...}
                    {"role": "tool", "results": [{"id", "content", "is_error"}]}
  tools   a list of {"name", "description", "input_schema"}
  reply   {"text", "tool_calls": [{"id", "name", "input"}], "stop", "usage", "opaque"}
          stop is "end" (the model is done), "tool" (it asks for tools),
          "limit" (cut off) or "refused".

"opaque" is whatever the provider wants handed back unchanged on the next call.
The agents never look inside it.

Connectors here:
  Scripted   a stand-in that replays prepared replies. Used by the tests, so they
             run every time, without a key and without cost. It is not a model.
  Claude     Anthropic's Messages API over plain HTTPS (standard library only).
             Written against the API reference as read on 18 November 2026.

The key is read from a file at the moment of the call and is never logged, printed
or stored in a run record.
"""
import json
import os
import urllib.error
import urllib.request
from pathlib import Path

KEY_FILE_VARIABLE = "SENTINEL_MODEL_KEY_FILE"  # the first name, kept so solution 02 runs as before
SHARED_KEY_FILE_VARIABLE = "HALDEN_MODEL_KEY_FILE"  # the name for every later solution


class ModelError(RuntimeError):
    """The model service could not be used. The loop stops; it never invents a reply."""


class Scripted:
    """Replays prepared replies in order and remembers what it was asked."""
    name = "scripted stand-in (no model)"

    def __init__(self, replies: list[dict]):
        self.replies = list(replies)
        self.asked: list[dict] = []

    def ask(self, system: str, turns: list[dict], tools: list[dict]) -> dict:
        self.asked.append({"system": system, "turns": json.loads(json.dumps(turns)),
                           "tools": [t["name"] for t in tools]})
        if not self.replies:
            raise ModelError("The scripted stand-in has no reply left")
        reply = self.replies.pop(0)
        calls = reply.get("tool_calls", [])
        return {"text": reply.get("text", ""), "tool_calls": calls,
                "stop": reply.get("stop", "tool" if calls else "end"),
                "usage": {"input": 0, "output": 0}, "opaque": None}


def _post(url: str, headers: dict, body: dict, timeout: int) -> dict:
    request = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"),
                                     headers=headers, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", "replace")[:300]
        raise ModelError(f"The model service answered {error.code}: {detail}") from None
    except (urllib.error.URLError, TimeoutError) as error:
        raise ModelError(f"The model service could not be reached: {error}") from None


class Claude:
    """Anthropic Messages API. Model, effort and limits are settings, not code."""
    STOPS = {"end_turn": "end", "stop_sequence": "end", "tool_use": "tool",
             "max_tokens": "limit", "model_context_window_exceeded": "limit", "refusal": "refused"}

    def __init__(self, model: str = "claude-fable-5-2", effort: str = "medium",
                 max_tokens: int = 16000, key_file: str | None = None,
                 url: str = "https://api.anthropic.com/v1/messages",
                 version: str = "2026-10-21", auth: str = "bearer",
                 timeout: int = 300, post=_post):
        self.model, self.effort, self.max_tokens = model, effort, max_tokens
        self.key_file = (key_file or os.environ.get(SHARED_KEY_FILE_VARIABLE, "")
                         or os.environ.get(KEY_FILE_VARIABLE, ""))
        self.url, self.version, self.auth = url, version, auth
        self.timeout, self._post = timeout, post
        self.name = f"{model}, effort {effort}"

    def _headers(self) -> dict:
        if not self.key_file:
            raise ModelError("No model key file. Put the key in a file and set "
                             f"{SHARED_KEY_FILE_VARIABLE} to its path (the older {KEY_FILE_VARIABLE} also works).")
        if not Path(self.key_file).is_file():
            raise ModelError(f"No model key file at '{self.key_file}'. That is the path in "
                             f"{SHARED_KEY_FILE_VARIABLE} or {KEY_FILE_VARIABLE}; check the file name.")
        key = Path(self.key_file).read_text(encoding="utf-8-sig").strip()  # utf-8-sig: Notepad may put a marker first
        credential = {"Authorization": f"Bearer {key}"} if self.auth == "bearer" else {"x-api-key": key}
        return {**credential, "anthropic-version": self.version, "content-type": "application/json"}

    @staticmethod
    def _messages(turns: list[dict]) -> list[dict]:
        messages = []
        for turn in turns:
            if turn["role"] == "user":
                messages.append({"role": "user", "content": turn["text"]})
            elif turn["role"] == "assistant":
                # Hand back exactly what the service sent (it requires this for its
                # reasoning blocks); rebuild only when the turn came from elsewhere.
                blocks = turn.get("opaque") or (
                    ([{"type": "text", "text": turn["text"]}] if turn.get("text") else [])
                    + [{"type": "tool_use", "id": c["id"], "name": c["name"], "input": c["input"]}
                       for c in turn.get("tool_calls", [])])
                messages.append({"role": "assistant", "content": blocks})
            else:
                messages.append({"role": "user", "content": [
                    {"type": "tool_result", "tool_use_id": r["id"], "content": r["content"],
                     "is_error": bool(r.get("is_error"))} for r in turn["results"]]})
        return messages

    def ask(self, system: str, turns: list[dict], tools: list[dict]) -> dict:
        body = {"model": self.model, "max_tokens": self.max_tokens, "system": system,
                "messages": self._messages(turns), "output_config": {"effort": self.effort}}
        if tools:
            body["tools"] = tools
        usage = {"input": 0, "output": 0}
        for _ in range(4):  # "pause_turn": the service asks to be called again with its own reply
            answer = self._post(self.url, self._headers(), body, self.timeout)
            used = answer.get("usage", {})
            usage["input"] += sum(used.get(k) or 0 for k in (
                "input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens"))
            usage["output"] += used.get("output_tokens") or 0
            if answer.get("stop_reason") != "pause_turn":
                break
            body["messages"] = body["messages"] + [{"role": "assistant", "content": answer["content"]}]
        else:
            raise ModelError("The model service paused four times in a row")
        blocks = answer.get("content", [])
        return {"text": "".join(b["text"] for b in blocks if b["type"] == "text"),
                "tool_calls": [{"id": b["id"], "name": b["name"], "input": b["input"]}
                               for b in blocks if b["type"] == "tool_use"],
                "stop": self.STOPS.get(answer.get("stop_reason"), "end"),
                "usage": usage, "opaque": blocks}
