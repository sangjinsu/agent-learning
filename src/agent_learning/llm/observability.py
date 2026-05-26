from __future__ import annotations

from dataclasses import dataclass

from langchain_core.messages import BaseMessage

from agent_learning.llm.prompting import chat_input, default_chat_prompt, is_blank_question


@dataclass(frozen=True)
class CallbackEvent:
    timing: str
    name: str
    component: str
    summary: str


@dataclass(frozen=True)
class ObservableChatResult:
    answer: str
    events: list[CallbackEvent]


class CallbackRecorder:
    def __init__(self) -> None:
        self.events: list[CallbackEvent] = []

    def start(self, name: str, component: str, summary: str) -> None:
        self.events.append(CallbackEvent("start", name, component, summary))

    def end(self, name: str, component: str, summary: str) -> None:
        self.events.append(CallbackEvent("end", name, component, summary))

    def error(self, name: str, component: str, summary: str) -> None:
        self.events.append(CallbackEvent("error", name, component, summary))


def run_observable_chat_chain(
    *,
    model,
    question: str,
    history: list[BaseMessage] | None = None,
) -> ObservableChatResult:
    if is_blank_question(question):
        raise ValueError("chat service: question must not be blank")
    if model is None:
        raise ValueError("observable chat chain: model is required")

    recorder = CallbackRecorder()
    variables = chat_input(question, history)
    prompt = default_chat_prompt()

    recorder.start("chain", "RunnableSequence", f"variables={sorted(variables)}")
    try:
        recorder.start("prompt", "ChatPromptTemplate", f"variables={sorted(variables)}")
        messages = prompt.format_messages(**variables)
        recorder.end("prompt", "ChatPromptTemplate", f"messages={len(messages)}")

        recorder.start("model", type(model).__name__, f"messages={len(messages)}")
        response = model.invoke(messages)
        recorder.end("model", type(model).__name__, f"content={_summarize(str(response.content))}")
        recorder.end("chain", "RunnableSequence", "ok")
    except Exception as exc:
        recorder.error("chain", "RunnableSequence", str(exc))
        raise

    return ObservableChatResult(answer=str(response.content), events=list(recorder.events))


def _summarize(content: str) -> str:
    content = " ".join(content.split())
    return content if len(content) <= 160 else content[:157] + "..."
