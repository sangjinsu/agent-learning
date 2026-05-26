from __future__ import annotations

from langchain_core.messages import BaseMessage

from agent_learning.llm.prompting import format_messages, is_blank_question


class ChatService:
    def __init__(self, model) -> None:
        self.model = model

    def ask(self, question: str) -> str:
        return self.ask_with_history(question, [])

    def ask_with_history(self, question: str, history: list[BaseMessage]) -> str:
        if is_blank_question(question):
            raise ValueError("chat service: question must not be blank")
        if self.model is None:
            raise ValueError("chat service: model is required")
        message = self.model.invoke(format_messages(question, history))
        return str(message.content)
