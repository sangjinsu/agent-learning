from __future__ import annotations

import sys

from agent_learning.example_support import (
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
    print(f"question: {question}")
    print_tool_schema(tools)
    print_messages("prompt messages", result.prompt_messages)
    print_tool_calls("model tool calls", result.first_response)
    print_messages("tool messages", result.tool_messages)
    print(f"final answer: {result.answer}")


if __name__ == "__main__":
    main()
