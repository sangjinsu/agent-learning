from __future__ import annotations

from langchain_core.messages import BaseMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

DEFAULT_SYSTEM_PROMPT = "You are a helpful LangGraph/LangChain tutor. Explain concepts clearly and keep answers concise."


def default_chat_prompt() -> ChatPromptTemplate:
    return ChatPromptTemplate.from_messages(
        [
            ("system", DEFAULT_SYSTEM_PROMPT),
            MessagesPlaceholder("history", optional=True),
            ("human", "{question}"),
        ]
    )


def format_messages(question: str, history: list[BaseMessage] | None = None) -> list[BaseMessage]:
    if is_blank_question(question):
        raise ValueError("chat service: question must not be blank")
    return default_chat_prompt().format_messages(question=question, history=history or [])


def chat_input(question: str, history: list[BaseMessage] | None = None) -> dict[str, object]:
    data: dict[str, object] = {"question": question}
    if history:
        data["history"] = list(history)
    return data


def is_blank_question(question: str) -> bool:
    return not question.strip()
