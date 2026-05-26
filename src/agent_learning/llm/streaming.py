from __future__ import annotations

from dataclasses import dataclass

from langchain_core.messages import BaseMessage

from agent_learning.llm.prompting import format_messages, is_blank_question


@dataclass(frozen=True)
class StreamingResult:
    prompt_messages: list[BaseMessage]
    chunks: list[str]
    answer: str


class StreamingService:
    def __init__(self, model) -> None:
        self.model = model

    def ask(self, question: str) -> StreamingResult:
        return self.ask_with_history(question, [])

    def ask_with_history(self, question: str, history: list[BaseMessage] | None) -> StreamingResult:
        if is_blank_question(question):
            raise ValueError("chat service: question must not be blank")
        if self.model is None:
            raise ValueError("chat service: model is required")
        messages = format_messages(question, history or [])
        chunks = [str(chunk.content) for chunk in self.model.stream(messages) if str(chunk.content)]
        return StreamingResult(prompt_messages=messages, chunks=chunks, answer="".join(chunks))
