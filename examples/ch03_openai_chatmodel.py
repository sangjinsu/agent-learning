from __future__ import annotations

import sys

from agent_learning.example_support import (
    parse_example_args,
    print_learning_sections,
    print_messages,
    print_model_selection,
    select_chat_model,
)
from agent_learning.llm.chat import ChatService
from agent_learning.llm.prompting import format_messages


def main() -> None:
    args = parse_example_args(sys.argv[1:], "What does provider ChatModel do?")
    question = args.question
    selection = select_chat_model("Fake OpenAI-style answer from chapter 03.")
    messages = format_messages(question)
    answer = ChatService(selection.model).ask(question)

    print("provider chatmodel:")
    print_model_selection(selection, verbose=args.verbose)
    print(f"question: {question}")
    if args.verbose:
        print_learning_sections(
            goal="같은 ChatService 경계에 fake model 또는 실제 provider ChatModel을 주입하는 방식을 확인합니다.",
            happens=[
                "환경 변수와 .env에서 provider 설정을 읽습니다.",
                "integration flag와 provider API key가 모두 있을 때만 실제 ChatModel을 생성합니다.",
                "그 외에는 fake fallback을 사용해 예제가 항상 안전하게 실행됩니다.",
            ],
            matters="외부 API 호출을 opt-in으로 만들면 unit test와 학습 실행이 비용, 네트워크, secret 상태에 의존하지 않습니다.",
            try_next=[
                "기본 fake mode와 RUN_AGENT_LEARNING_INTEGRATION=1 mode의 config 출력을 비교해 보세요.",
                "AGENT_LEARNING_PROVIDER, OPENAI_MODEL, ANTHROPIC_MODEL 값을 바꾸면 config 출력이 어떻게 달라지는지 확인해 보세요.",
            ],
        )
        print_messages("prompt messages", messages)
    print(f"final answer: {answer}")


if __name__ == "__main__":
    main()
