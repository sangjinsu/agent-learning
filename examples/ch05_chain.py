from __future__ import annotations

import sys

from agent_learning.example_support import (
    parse_example_args,
    print_learning_sections,
    print_mapping,
    print_messages,
    print_model_response,
    print_model_selection,
    select_chat_model,
)
from agent_learning.llm.chain import ChainService


def main() -> None:
    args = parse_example_args(sys.argv[1:], "How does Chain work?")
    question = args.question
    selection = select_chat_model("Chain response from chapter 05.")
    trace = ChainService(selection.model).ask_with_trace(question)

    print("chain:")
    print_model_selection(selection, verbose=args.verbose)
    print(f"question: {question}")
    print(f"prompt message count: {len(trace.prompt_messages)}")
    if args.verbose:
        print_learning_sections(
            goal="ChatPromptTemplate과 ChatModel을 runnable chain으로 연결한 선형 흐름을 확인합니다.",
            happens=[
                "input variables가 prompt로 들어가 message 목록을 만듭니다.",
                "prompt | model 형태의 chain은 같은 단계를 하나의 runnable처럼 실행합니다.",
                "trace는 chain 내부의 input, prompt messages, model response를 분리해서 보여줍니다.",
            ],
            matters="선형 흐름은 Graph보다 단순하고 읽기 쉬워, 조건 분기가 없는 LLM 기능의 기본 단위로 적합합니다.",
            try_next=[
                "history를 넣는 ask_with_history() 경로와 trace 출력의 차이를 비교해 보세요.",
                "Chapter 06의 graph 출력과 비교해 언제 chain만으로 충분한지 생각해 보세요.",
            ],
        )
        print_mapping("input variables", trace.input_variables)
        print_messages("prompt messages", trace.prompt_messages)
        print_model_response("model response", trace.model_response)
    print(f"final answer: {trace.answer}")


if __name__ == "__main__":
    main()
