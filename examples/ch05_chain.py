from __future__ import annotations

import sys

from agent_learning.example_support import (
    print_mapping,
    print_messages,
    print_model_response,
    print_model_selection,
    select_chat_model,
)
from agent_learning.llm.chain import ChainService


def main() -> None:
    question = " ".join(sys.argv[1:]) or "How does Chain work?"
    selection = select_chat_model("Chain response from chapter 05.")
    trace = ChainService(selection.model).ask_with_trace(question)

    print_model_selection(selection)
    print_mapping("input variables", trace.input_variables)
    print_messages("prompt messages", trace.prompt_messages)
    print_model_response("model response", trace.model_response)
    print(f"final answer: {trace.answer}")


if __name__ == "__main__":
    main()
