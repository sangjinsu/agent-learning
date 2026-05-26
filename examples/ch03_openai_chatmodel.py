from __future__ import annotations

import sys

from agent_learning.example_support import (
    print_learning_sections,
    print_messages,
    print_model_selection,
    select_chat_model,
)
from agent_learning.llm.chat import ChatService
from agent_learning.llm.prompting import format_messages


def main() -> None:
    question = " ".join(sys.argv[1:]) or "What does ChatOpenAI do?"
    selection = select_chat_model("Fake OpenAI-style answer from chapter 03.")
    messages = format_messages(question)
    answer = ChatService(selection.model).ask(question)

    print_model_selection(selection)
    print_learning_sections(
        goal="같은 ChatService 경계에 fake model 또는 ChatOpenAI를 주입하는 방식을 확인합니다.",
        happens=[
            "환경 변수와 .env에서 OpenAI 설정을 읽습니다.",
            "integration flag와 API key가 모두 있을 때만 실제 ChatOpenAI를 생성합니다.",
            "그 외에는 fake fallback을 사용해 예제가 항상 안전하게 실행됩니다.",
        ],
        matters="외부 API 호출을 opt-in으로 만들면 unit test와 학습 실행이 비용, 네트워크, secret 상태에 의존하지 않습니다.",
        try_next=[
            "기본 fake mode와 RUN_AGENT_LEARNING_INTEGRATION=1 mode의 config 출력을 비교해 보세요.",
            "OPENAI_MODEL 값을 바꾸면 config에 어떤 모델명이 표시되는지 확인해 보세요.",
        ],
    )
    print(f"question: {question}")
    print_messages("prompt messages", messages)
    print(f"final answer: {answer}")


if __name__ == "__main__":
    main()
