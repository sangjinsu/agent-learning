from __future__ import annotations

import sys

from agent_learning.llm.prompting import format_messages


def main() -> None:
    question = " ".join(sys.argv[1:]) or "How does ChatPromptTemplate work?"
    for message in format_messages(question):
        print(f"{message.type}: {message.content}")


if __name__ == "__main__":
    main()
