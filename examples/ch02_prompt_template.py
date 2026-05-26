from __future__ import annotations

import sys

from langchain_core.messages import AIMessage, HumanMessage

from agent_learning.example_support import print_learning_sections, print_mapping, print_messages
from agent_learning.llm.prompting import chat_input, format_messages


def main() -> None:
    question = " ".join(sys.argv[1:]) or "How does ChatPromptTemplate work?"
    history = [
        HumanMessage(content="What did Chapter 01 cover?"),
        AIMessage(content="It covered a replaceable ChatModel boundary."),
    ]
    variables = chat_input(question, history)
    messages = format_messages(question, history)

    print("mode: local prompt formatting")
    print_learning_sections(
        goal="입력 변수와 history가 ChatPromptTemplate을 거쳐 role이 있는 message 목록으로 바뀌는 과정을 봅니다.",
        happens=[
            "chat_input()이 question과 optional history를 dict 형태로 준비합니다.",
            "ChatPromptTemplate은 system, history, human message 순서를 고정합니다.",
            "formatted messages 출력에서 최종적으로 model에 전달될 role/content를 확인합니다.",
        ],
        matters="Prompt template을 먼저 명시하면 model 교체나 chain 확장 후에도 입력 구조가 흔들리지 않습니다.",
        try_next=[
            "history 항목을 하나 더 추가하고 formatted messages의 순서를 확인해 보세요.",
            '질문을 한국어로 바꿔 실행해 보세요: uv run python examples/ch02_prompt_template.py "프롬프트 템플릿은 왜 필요한가요?"',
        ],
    )
    print_mapping("input variables", variables)
    print_messages("formatted messages", messages)


if __name__ == "__main__":
    main()
