from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Iterable, Mapping

from langchain_core.messages import BaseMessage
from langchain_core.tools import BaseTool

from agent_learning.fake import FakeChatModel, FakeStreamingChatModel
from agent_learning.llm.openai import (
    OpenAIConfig,
    integration_enabled,
    load_config_from_env,
    new_chat_model,
)


@dataclass(frozen=True)
class ExampleModelSelection:
    mode: str
    model: Any
    config: OpenAIConfig
    integration_requested: bool


def select_chat_model(fake_response: str) -> ExampleModelSelection:
    config = load_config_from_env()
    requested = integration_enabled()
    if requested and config.api_key.strip():
        return ExampleModelSelection("openai", new_chat_model(config), config, requested)
    return ExampleModelSelection("fake", FakeChatModel(fake_response), config, requested)


def select_streaming_model(*fake_chunks: str) -> ExampleModelSelection:
    config = load_config_from_env()
    requested = integration_enabled()
    if requested and config.api_key.strip():
        return ExampleModelSelection("openai", new_chat_model(config), config, requested)
    return ExampleModelSelection("fake", FakeStreamingChatModel(*fake_chunks), config, requested)


def print_learning_sections(
    *,
    goal: str,
    happens: Iterable[str],
    matters: str,
    try_next: Iterable[str],
) -> None:
    print(f"learning goal: {goal}")
    print("what happens:")
    for item in happens:
        print(f"- {item}")
    print(f"why it matters: {matters}")
    print("try next:")
    for item in try_next:
        print(f"- {item}")


def print_model_selection(selection: ExampleModelSelection) -> None:
    print(f"mode: {selection.mode}")
    print("config:")
    print(f"- integration_requested: {_bool_text(selection.integration_requested)}")
    print(f"- openai_model: {selection.config.model}")
    print(f"- openai_base_url: {selection.config.base_url or '(default)'}")
    print(f"- openai_api_key_set: {_bool_text(bool(selection.config.api_key.strip()))}")
    if selection.mode == "fake":
        if selection.integration_requested:
            print("- note: OpenAI integration requested but OPENAI_API_KEY is missing. Using fake fallback.")
        else:
            print(
                "- note: OpenAI integration is disabled. Using fake fallback. "
                "Set RUN_AGENT_LEARNING_INTEGRATION=1 and OPENAI_API_KEY to call OpenAI."
            )


def print_mapping(label: str, values: Mapping[str, object]) -> None:
    print(f"{label}:")
    if not values:
        print("- none")
        return
    for key in sorted(values):
        print(f"- {key}: {_format_value(values[key])}")


def print_messages(label: str, messages: Iterable[BaseMessage]) -> None:
    print(f"{label}:")
    count = 0
    for index, message in enumerate(messages):
        count += 1
        print(f"- [{index}] {message.type}: {_summarize(message.content)}")
    if count == 0:
        print("- none")


def print_tool_schema(tools: Iterable[BaseTool]) -> None:
    print("tool schema:")
    count = 0
    for tool in tools:
        count += 1
        print(f"- name: {tool.name}")
        print(f"  description: {_summarize(tool.description)}")
        print(f"  args: {_json(tool.args)}")
    if count == 0:
        print("- none")


def print_tool_calls(label: str, message: BaseMessage) -> None:
    print(f"{label}:")
    calls = getattr(message, "tool_calls", []) or []
    if not calls:
        print("- none")
        return
    for index, call in enumerate(calls):
        print(f"- [{index}] {_json(call)}")


def print_model_response(label: str, message: BaseMessage | None) -> None:
    print(f"{label}:")
    if message is None:
        print("- none")
        return
    print(f"- type: {message.type}")
    print(f"- content: {_summarize(message.content)}")


def print_key_values(label: str, values: Mapping[str, object]) -> None:
    print(f"{label}:")
    if not values:
        print("- none")
        return
    for key, value in values.items():
        print(f"- {key}: {_format_value(value)}")


def _format_value(value: object) -> str:
    if isinstance(value, list) and all(isinstance(item, BaseMessage) for item in value):
        return f"{len(value)} messages"
    if isinstance(value, BaseMessage):
        return f"{value.type}: {_summarize(value.content)}"
    if isinstance(value, (dict, list, tuple)):
        return _json(value)
    return _summarize(value)


def _summarize(value: object, limit: int = 220) -> str:
    text = " ".join(str(value).split())
    return text if len(text) <= limit else text[: limit - 3] + "..."


def _json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, default=str)


def _bool_text(value: bool) -> str:
    return "true" if value else "false"
