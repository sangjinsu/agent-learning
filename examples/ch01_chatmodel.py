from __future__ import annotations

import sys

from agent_learning.example_support import parse_example_args, print_learning_sections, print_messages
from agent_learning.fake import FakeChatModel
from agent_learning.llm.chat import ChatService
from agent_learning.llm.prompting import format_messages


def main() -> None:
    args = parse_example_args(sys.argv[1:], "What is LangChain?")
    question = args.question
    model = FakeChatModel("Fake answer from chapter 01.")
    messages = format_messages(question)
    answer = ChatService(model).ask(question)

    print("chatmodel:")
    print("mode: fake")
    print(f"question: {question}")
    if args.verbose:
        print_learning_sections(
            goal="ChatModel을 교체 가능한 경계로 두고 질문/응답 흐름을 확인합니다.",
            happens=[
                "ChatService가 사용자의 question을 prompt messages로 바꿉니다.",
                "FakeChatModel이 외부 API 없이 deterministic answer를 반환합니다.",
                "model.last_input을 테스트하면 실제 model에 들어간 message 순서를 검증할 수 있습니다.",
            ],
            matters="처음부터 실제 LLM을 호출하지 않아도 애플리케이션의 service boundary를 안정적으로 설계하고 테스트할 수 있습니다.",
            try_next=[
                '질문을 바꿔 실행해 보세요: uv run python examples/ch01_chatmodel.py "Explain agents in one sentence"',
                "FakeChatModel의 응답 문자열을 바꿔도 ChatService 코드는 그대로 동작하는지 확인해 보세요.",
            ],
        )
        print_messages("prompt messages", messages)
    print(f"final answer: {answer}")


if __name__ == "__main__":
    main()
