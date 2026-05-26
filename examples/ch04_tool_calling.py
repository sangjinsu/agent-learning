from __future__ import annotations

import sys

from agent_learning.example_support import (
    print_learning_sections,
    print_messages,
    print_model_selection,
    print_tool_calls,
    print_tool_schema,
    select_chat_model,
)
from agent_learning.llm.toolcalling import ToolCallingService
from agent_learning.tools.calculator import calculator_tool


def main() -> None:
    question = " ".join(sys.argv[1:]) or "12 * (7 + 3)"
    selection = select_chat_model("Tool calling fallback response.")
    tools = [calculator_tool()]
    result = ToolCallingService(selection.model).ask(question, tools)

    print_model_selection(selection)
    print_learning_sections(
        goal="model이 직접 계산하지 않고 tool schema를 보고 calculator tool을 요청하는 loop를 관찰합니다.",
        happens=[
            "calculator tool의 name, description, args schema를 model에 제공합니다.",
            "model의 첫 응답에서 tool_calls가 나오면 allowlist에 있는 tool만 실행합니다.",
            "tool 실행 결과는 ToolMessage로 다시 대화에 추가되고 model이 final answer를 만듭니다.",
        ],
        matters="LLM이 잘 못하는 deterministic 작업은 tool로 분리하면 정확도와 안전성을 동시에 높일 수 있습니다.",
        try_next=[
            '다른 산술식을 넣어 보세요: uv run python examples/ch04_tool_calling.py "18 / (2 + 1)"',
            "calculator가 지원하지 않는 표현식을 넣으면 어느 계층에서 거부되는지 테스트를 따라가 보세요.",
        ],
    )
    print(f"question: {question}")
    print_tool_schema(tools)
    print_messages("prompt messages", result.prompt_messages)
    print_tool_calls("model tool calls", result.first_response)
    print_messages("tool messages", result.tool_messages)
    print(f"final answer: {result.answer}")


if __name__ == "__main__":
    main()
