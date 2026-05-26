from __future__ import annotations

import sys

from agent_learning.example_support import print_learning_sections, print_model_selection, select_chat_model
from agent_learning.llm.observability import run_observable_chat_chain


def main() -> None:
    question = " ".join(sys.argv[1:]) or "How do callbacks help?"
    selection = select_chat_model("Observable response from chapter 08.")
    result = run_observable_chat_chain(model=selection.model, question=question)

    print_model_selection(selection)
    print_learning_sections(
        goal="prompt와 model 실행 전후에 callback event가 어떻게 쌓이는지 관찰합니다.",
        happens=[
            "chain start event가 input variables를 기록합니다.",
            "prompt start/end event가 message formatting 단계를 감쌉니다.",
            "model start/end event가 model 호출과 응답 요약을 기록합니다.",
        ],
        matters="Callback은 답변을 바꾸지 않고 실행 과정을 설명해 주므로, RAG나 agent workflow를 디버깅할 때 근거 추적에 유용합니다.",
        try_next=[
            "callback events의 순서를 chain -> prompt -> model -> chain 흐름으로 따라가 보세요.",
            "Chapter 09 RAG 예제에서 retrieved context가 model에 들어가는 흐름과 연결해 보세요.",
        ],
    )
    print(f"question: {question}")
    print("callback events:")
    for index, event in enumerate(result.events):
        print(f"- [{index}] {event.timing} {event.name} ({event.component}): {event.summary}")
    if not result.events:
        print("- none")
    print(f"final answer: {result.answer}")


if __name__ == "__main__":
    main()
