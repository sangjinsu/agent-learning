from __future__ import annotations

from dataclasses import dataclass

from langchain_core.messages import BaseMessage

from agent_learning.llm.prompting import chat_input, default_chat_prompt, is_blank_question


@dataclass(frozen=True)
class ChainTrace:
    input_variables: dict[str, object]
    prompt_messages: list[BaseMessage]
    model_response: BaseMessage

    @property
    def answer(self) -> str:
        return str(self.model_response.content)


class ChainService:
    def __init__(self, model) -> None:
        if model is None:
            raise ValueError("chat chain: model is required")
        self.model = model
        self.prompt = default_chat_prompt()
        self.chain = self.prompt | self.model

    def ask(self, question: str) -> str:
        return self.ask_with_history(question, [])

    def ask_with_history(self, question: str, history: list[BaseMessage] | None) -> str:
        if is_blank_question(question):
            raise ValueError("chat service: question must not be blank")
        message = self.chain.invoke(chat_input(question, history))
        return str(message.content)

    def ask_with_trace(self, question: str, history: list[BaseMessage] | None = None) -> ChainTrace:
        if is_blank_question(question):
            raise ValueError("chat service: question must not be blank")
        variables = chat_input(question, history)
        prompt_messages = self.prompt.format_messages(**variables)
        model_response = self.model.invoke(prompt_messages)
        return ChainTrace(variables, prompt_messages, model_response)
