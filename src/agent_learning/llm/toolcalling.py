from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from typing import Any

from langchain_core.messages import BaseMessage, ToolMessage
from langchain_core.tools import BaseTool

from agent_learning.llm.prompting import format_messages, is_blank_question


@dataclass(frozen=True)
class ToolCallingResult:
    prompt_messages: list[BaseMessage]
    first_response: BaseMessage
    tool_messages: list[ToolMessage]
    final_response: BaseMessage

    @property
    def answer(self) -> str:
        return str(self.final_response.content)


class ToolCallingService:
    def __init__(self, model) -> None:
        self.model = model

    def ask(self, question: str, allowed_tools: list[BaseTool]) -> ToolCallingResult:
        return self.ask_with_history_and_tools(question, [], allowed_tools)

    def ask_with_history_and_tools(
        self,
        question: str,
        history: list[BaseMessage] | None,
        allowed_tools: list[BaseTool],
    ) -> ToolCallingResult:
        if is_blank_question(question):
            raise ValueError("chat service: question must not be blank")
        if self.model is None:
            raise ValueError("chat service: model is required")
        if not hasattr(self.model, "bind_tools"):
            raise ValueError("chat service: model must support tool calling")

        messages = format_messages(question, history or [])
        model_with_tools = self.model.bind_tools(allowed_tools)
        first_response = model_with_tools.invoke(messages)
        tool_calls = getattr(first_response, "tool_calls", []) or []
        if not tool_calls:
            return ToolCallingResult(messages, first_response, [], first_response)

        tool_by_name = {tool.name: tool for tool in allowed_tools}
        tool_messages = [_execute_tool_call(tool_by_name, call) for call in tool_calls]
        final_response = model_with_tools.invoke([*messages, first_response, *tool_messages])
        return ToolCallingResult(messages, first_response, tool_messages, final_response)


def _execute_tool_call(tool_by_name: dict[str, BaseTool], call: dict[str, Any]) -> ToolMessage:
    name = call["name"]
    if name not in tool_by_name:
        raise ValueError(f"chat service: tool is not allowed: {name}")
    result = tool_by_name[name].invoke(call.get("args", {}))
    return ToolMessage(
        content=_json_content(result),
        tool_call_id=call.get("id") or name,
        name=name,
    )


def _json_content(value: Any) -> str:
    if hasattr(value, "__dataclass_fields__"):
        value = asdict(value)
    return json.dumps(value, ensure_ascii=False, sort_keys=True)
