from __future__ import annotations

import sys

from agent_learning.example_support import print_messages
from agent_learning.fake import FakeChatModel
from agent_learning.llm.chat import ChatService
from agent_learning.llm.prompting import format_messages


def main() -> None:
    question = " ".join(sys.argv[1:]) or "What is LangChain?"
    model = FakeChatModel("Fake answer from chapter 01.")
    messages = format_messages(question)
    answer = ChatService(model).ask(question)

    print("mode: fake")
    print(f"question: {question}")
    print_messages("prompt messages", messages)
    print(f"final answer: {answer}")


if __name__ == "__main__":
    main()
