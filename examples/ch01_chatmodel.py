from __future__ import annotations

import sys

from agent_learning.fake import FakeChatModel
from agent_learning.llm.chat import ChatService


def main() -> None:
    question = " ".join(sys.argv[1:]) or "What is LangChain?"
    print(ChatService(FakeChatModel("Fake answer from chapter 01.")).ask(question))


if __name__ == "__main__":
    main()
