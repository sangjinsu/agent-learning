from __future__ import annotations

import sys

from agent_learning.example_support import (
    print_messages,
    print_model_selection,
    select_chat_model,
)
from agent_learning.llm.chat import ChatService
from agent_learning.llm.prompting import format_messages


def main() -> None:
    question = " ".join(sys.argv[1:]) or "What does ChatOpenAI do?"
    selection = select_chat_model("Fake OpenAI-style answer from chapter 03.")
    messages = format_messages(question)
    answer = ChatService(selection.model).ask(question)

    print_model_selection(selection)
    print(f"question: {question}")
    print_messages("prompt messages", messages)
    print(f"final answer: {answer}")


if __name__ == "__main__":
    main()
