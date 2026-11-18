"""The model connector, tested without a network and without a key.

The Claude connector is given a stand-in for the HTTPS call, so these tests check
what would be sent and how an answer is read. They do not prove the service accepts
it: that is shown only by a recorded real run.
"""
import json

import pytest

from sentinel.model import Claude, ModelError, Scripted

TOOL = {"name": "price_response", "description": "Price one response in lost output.",
        "input_schema": {"type": "object", "properties": {"points": {"type": "array"}}, "required": ["points"]}}


def answer(content, stop="end_turn", tokens=(100, 20)):
    return {"type": "message", "role": "assistant", "content": content, "stop_reason": stop,
            "usage": {"input_tokens": tokens[0], "output_tokens": tokens[1],
                      "cache_creation_input_tokens": None, "cache_read_input_tokens": 5}}


class Wire:
    """Stands in for the HTTPS call and keeps what was sent."""
    def __init__(self, *answers):
        self.answers, self.sent = list(answers), []

    def __call__(self, url, headers, body, timeout):
        self.sent.append({"url": url, "headers": headers, "body": json.loads(json.dumps(body))})
        return self.answers.pop(0)


@pytest.fixture
def key_file(tmp_path):
    path = tmp_path / "key.txt"
    path.write_text("test-key-not-real\n", encoding="utf-8")
    return str(path)


# -- the scripted stand-in ----------------------------------------------------
def test_scripted_replays_in_order_and_records_what_it_was_asked():
    model = Scripted([{"tool_calls": [{"id": "c1", "name": "price_response", "input": {"points": []}}]},
                      {"text": "done"}])
    first = model.ask("brief", [{"role": "user", "text": "go"}], [TOOL])
    second = model.ask("brief", [{"role": "user", "text": "go"}], [TOOL])
    assert first["stop"] == "tool" and first["tool_calls"][0]["name"] == "price_response"
    assert second == {"text": "done", "tool_calls": [], "stop": "end",
                      "usage": {"input": 0, "output": 0}, "opaque": None}
    assert model.asked[0]["system"] == "brief" and model.asked[0]["tools"] == ["price_response"]


def test_scripted_fails_loudly_when_it_runs_out():
    with pytest.raises(ModelError):
        Scripted([]).ask("brief", [], [])


# -- the Claude connector -----------------------------------------------------
def test_request_carries_model_effort_system_and_tools(key_file):
    wire = Wire(answer([{"type": "text", "text": "ok"}]))
    Claude(key_file=key_file, post=wire).ask("You are the planner.", [{"role": "user", "text": "go"}], [TOOL])
    sent = wire.sent[0]
    assert sent["url"] == "https://api.anthropic.com/v1/messages"
    assert sent["body"]["model"] == "claude-fable-5-2"
    assert sent["body"]["output_config"] == {"effort": "medium"}
    assert sent["body"]["system"] == "You are the planner."
    assert sent["body"]["messages"] == [{"role": "user", "content": "go"}]
    assert sent["body"]["tools"] == [TOOL]
    assert sent["headers"]["Authorization"] == "Bearer test-key-not-real"
    assert sent["headers"]["anthropic-version"] == "2026-10-21"


def test_the_other_way_of_sending_the_key_is_a_setting(key_file):
    wire = Wire(answer([{"type": "text", "text": "ok"}]))
    Claude(key_file=key_file, auth="x-api-key", post=wire).ask("s", [{"role": "user", "text": "go"}], [])
    assert wire.sent[0]["headers"]["x-api-key"] == "test-key-not-real"
    assert "Authorization" not in wire.sent[0]["headers"]
    assert "tools" not in wire.sent[0]["body"]


def test_a_tool_request_is_read_and_the_reply_is_handed_back_unchanged(key_file):
    thinking = {"type": "thinking", "thinking": "...", "signature": "sig"}
    use = {"type": "tool_use", "id": "toolu_1", "name": "price_response", "input": {"points": ["cut-cell-b2"]}}
    wire = Wire(answer([thinking, {"type": "text", "text": "Pricing."}, use], stop="tool_use"),
                answer([{"type": "text", "text": "EUR 120,000."}]))
    model = Claude(key_file=key_file, post=wire)
    turns = [{"role": "user", "text": "go"}]
    reply = model.ask("s", turns, [TOOL])
    assert reply["stop"] == "tool" and reply["text"] == "Pricing."
    assert reply["tool_calls"] == [{"id": "toolu_1", "name": "price_response", "input": {"points": ["cut-cell-b2"]}}]
    assert reply["usage"] == {"input": 105, "output": 20}

    turns += [{"role": "assistant", **reply},
              {"role": "tool", "results": [{"id": "toolu_1", "content": '{"cost_eur": 120000}'}]}]
    model.ask("s", turns, [TOOL])
    messages = wire.sent[1]["body"]["messages"]
    assert messages[1] == {"role": "assistant", "content": [thinking, {"type": "text", "text": "Pricing."}, use]}
    assert messages[2] == {"role": "user", "content": [
        {"type": "tool_result", "tool_use_id": "toolu_1", "content": '{"cost_eur": 120000}', "is_error": False}]}


def test_an_assistant_turn_from_another_source_is_rebuilt(key_file):
    wire = Wire(answer([{"type": "text", "text": "ok"}]))
    turns = [{"role": "user", "text": "go"},
             {"role": "assistant", "text": "Pricing.", "opaque": None,
              "tool_calls": [{"id": "c1", "name": "price_response", "input": {"points": []}}]},
             {"role": "tool", "results": [{"id": "c1", "content": "refused", "is_error": True}]}]
    Claude(key_file=key_file, post=wire).ask("s", turns, [TOOL])
    messages = wire.sent[0]["body"]["messages"]
    assert messages[1]["content"] == [{"type": "text", "text": "Pricing."},
                                      {"type": "tool_use", "id": "c1", "name": "price_response", "input": {"points": []}}]
    assert messages[2]["content"][0]["is_error"] is True


@pytest.mark.parametrize("reason, stop", [("end_turn", "end"), ("tool_use", "tool"), ("max_tokens", "limit"),
                                          ("model_context_window_exceeded", "limit"), ("refusal", "refused")])
def test_every_documented_stop_reason_is_understood(key_file, reason, stop):
    wire = Wire(answer([{"type": "text", "text": "x"}], stop=reason))
    assert Claude(key_file=key_file, post=wire).ask("s", [{"role": "user", "text": "go"}], [])["stop"] == stop


def test_a_paused_turn_is_continued_and_its_tokens_counted(key_file):
    wire = Wire(answer([{"type": "text", "text": "part"}], stop="pause_turn"),
                answer([{"type": "text", "text": "whole"}]))
    reply = Claude(key_file=key_file, post=wire).ask("s", [{"role": "user", "text": "go"}], [])
    assert reply["text"] == "whole" and reply["usage"] == {"input": 210, "output": 40}
    assert wire.sent[1]["body"]["messages"][-1] == {"role": "assistant", "content": [{"type": "text", "text": "part"}]}


def test_without_a_key_file_nothing_is_sent(tmp_path, monkeypatch):
    monkeypatch.delenv("SENTINEL_MODEL_KEY_FILE", raising=False)
    wire = Wire()
    with pytest.raises(ModelError):
        Claude(post=wire).ask("s", [{"role": "user", "text": "go"}], [])
    with pytest.raises(ModelError):
        Claude(key_file=str(tmp_path / "missing.txt"), post=wire).ask("s", [{"role": "user", "text": "go"}], [])
    assert wire.sent == []


def test_the_key_never_appears_in_a_reply(key_file):
    wire = Wire(answer([{"type": "text", "text": "ok"}]))
    reply = Claude(key_file=key_file, post=wire).ask("s", [{"role": "user", "text": "go"}], [])
    assert "test-key-not-real" not in json.dumps(reply)
