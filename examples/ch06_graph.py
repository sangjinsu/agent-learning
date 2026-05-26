from __future__ import annotations

import sys

from agent_learning.example_support import (
    print_key_values,
    print_messages,
    print_model_response,
    print_model_selection,
    select_chat_model,
)
from agent_learning.llm.graph import GraphInput, GraphService


def main() -> None:
    question = " ".join(sys.argv[1:]) or "calculate: 7 * (8 + 2)"
    selection = select_chat_model("Graph chat response from chapter 06.")
    result = GraphService(selection.model).run(GraphInput(question=question))

    print_model_selection(selection)
    print("graph:")
    print("- START -> route")
    print("- route -> calculator when the input is arithmetic")
    print("- route -> prompt -> model when the input is chat")
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
    if result.prompt_messages is not None:
        print_messages("prompt messages", result.prompt_messages)
    print_model_response("model response", result.model_response)
    print(f"final answer: {result.answer}")


if __name__ == "__main__":
    main()
