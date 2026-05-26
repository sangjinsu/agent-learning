from __future__ import annotations

import sys

from langchain_core.messages import AIMessage, HumanMessage

from agent_learning.example_support import print_mapping, print_messages
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
    print_mapping("input variables", variables)
    print_messages("formatted messages", messages)


if __name__ == "__main__":
    main()
