from __future__ import annotations

import json
import re
from dataclasses import replace
from typing import Any, Iterable, Iterator, Sequence

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, AIMessageChunk, BaseMessage, HumanMessage, ToolMessage
from langchain_core.outputs import ChatGeneration, ChatGenerationChunk, ChatResult
from langchain_core.tools import BaseTool


class FakeChatModel(BaseChatModel):
    """Deterministic chat model for unit tests and early learning chapters."""

    response: str = "fake answer"
    bound_tools: tuple[BaseTool, ...] = ()
    last_input: list[BaseMessage] = []
    generate_calls: int = 0

    def __init__(self, response: str = "fake answer", **kwargs: Any) -> None:
        super().__init__(response=response, **kwargs)

    @property
    def _llm_type(self) -> str:
        return "agent-learning-fake-chat"

    def bind_tools(self, tools: Sequence[BaseTool | type | dict[str, Any]], **kwargs: Any) -> "FakeChatModel":
        _ = kwargs
        copied = self.model_copy()
        copied.bound_tools = tuple(tool for tool in tools if isinstance(tool, BaseTool))
        return copied

    def _generate(
        self,
        messages: list[BaseMessage],
        stop: list[str] | None = None,
        run_manager: Any | None = None,
        **kwargs: Any,
    ) -> ChatResult:
        _ = stop, run_manager, kwargs
        self._validate_input(messages)
        self.last_input = list(messages)
        self.generate_calls += 1
        return ChatResult(generations=[ChatGeneration(message=self._next_message(messages))])

    def _next_message(self, messages: list[BaseMessage]) -> AIMessage:
        tool_messages = [message for message in messages if isinstance(message, ToolMessage)]
        if tool_messages:
            return AIMessage(content=_final_answer_from_tool_message(tool_messages[-1]))

        if self.bound_tools:
            expression = _extract_expression(messages[-1].content)
            if expression and any(tool.name == "calculator" for tool in self.bound_tools):
                return AIMessage(
                    content="",
                    tool_calls=[
                        {
                            "name": "calculator",
                            "args": {"expression": expression},
                            "id": "call_calculator_1",
                        }
                    ],
                )

        return AIMessage(content=self.response)

    @staticmethod
    def _validate_input(messages: list[BaseMessage]) -> None:
        if not messages:
            raise ValueError("fake chat model: input messages are required")
        last = messages[-1]
        if not isinstance(last, (HumanMessage, ToolMessage)) or not str(last.content).strip():
            raise ValueError("fake chat model: last user/tool message must not be blank")


class FakeStreamingChatModel(FakeChatModel):
    """Fake model that streams predefined chunks."""

    chunks: tuple[str, ...] = ()
    stream_calls: int = 0

    def __init__(self, *chunks: str) -> None:
        super().__init__(response="".join(chunks))
        self.chunks = tuple(chunks)

    @property
    def _llm_type(self) -> str:
        return "agent-learning-fake-streaming-chat"

    def _stream(
        self,
        messages: list[BaseMessage],
        stop: list[str] | None = None,
        run_manager: Any | None = None,
        **kwargs: Any,
    ) -> Iterator[ChatGenerationChunk]:
        _ = stop, run_manager, kwargs
        self._validate_input(messages)
        self.last_input = list(messages)
        self.stream_calls += 1
        for chunk in self.chunks:
            yield ChatGenerationChunk(message=AIMessageChunk(content=chunk))


def _extract_expression(content: Any) -> str:
    text = str(content).strip()
    lower = text.lower()
    for prefix in ("calculate:", "calc:", "calculate ", "calc "):
        if lower.startswith(prefix):
            return text[len(prefix) :].strip()
    if re.fullmatch(r"[\d\s+\-*/().]+", text):
        return text
    return ""


def _final_answer_from_tool_message(message: ToolMessage) -> str:
    try:
        payload = json.loads(str(message.content))
    except json.JSONDecodeError:
        return str(message.content)

    if "expression" in payload and "result" in payload:
        return f"{payload['expression']} = {_format_number(payload['result'])}"
    return str(message.content)


def _format_number(value: Any) -> str:
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)
