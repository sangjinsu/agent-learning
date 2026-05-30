from __future__ import annotations

import sys

from agent_learning.example_support import (
    parse_example_args,
    print_key_values,
    print_learning_sections,
    print_messages,
    print_model_response,
    print_model_selection,
    select_chat_model,
)
from agent_learning.llm.graph import GraphInput, GraphService


def main() -> None:
    args = parse_example_args(sys.argv[1:], "calculate: 7 * (8 + 2)")
    question = args.question
    selection = select_chat_model("Graph chat response from chapter 06.")
    result = GraphService(selection.model).run(GraphInput(question=question))

    print("graph:")
    print_model_selection(selection, verbose=args.verbose)
    print(f"question: {question}")
    print(f"selected route: {result.route}")
    if result.calculation is not None:
        print_key_values(
            "calculation",
            {
                "expression": result.calculation.expression,
                "result": result.calculation.result,
            },
        )
    if args.verbose:
        print_learning_sections(
            goal="LangGraph StateGraph가 입력에 따라 calculator branch와 chat branch 중 하나를 선택하는 과정을 봅니다.",
            happens=[
                "route node가 question을 검사해 계산식인지 일반 대화인지 분류합니다.",
                "calculator route는 local tool을 직접 실행하므로 model을 호출하지 않습니다.",
                "chat route는 prompt node와 model node를 거쳐 assistant answer를 생성합니다.",
            ],
            matters="Graph는 조건 분기, tool routing, 여러 실행 경로가 필요한 agent workflow를 명시적으로 표현할 수 있습니다.",
            try_next=[
                'chat route를 보려면 일반 질문을 넣어 보세요: uv run python examples/ch06_graph.py "What is LangGraph?"',
                "계산 질문에서는 model response가 none인 이유를 graph edge와 연결해서 확인해 보세요.",
            ],
        )
        print("- START -> route")
        print("- route -> calculator when the input is arithmetic")
        print("- route -> prompt -> model when the input is chat")
        if result.prompt_messages is not None:
            print_messages("prompt messages", result.prompt_messages)
        print_model_response("model response", result.model_response)
    print(f"final answer: {result.answer}")


if __name__ == "__main__":
    main()
