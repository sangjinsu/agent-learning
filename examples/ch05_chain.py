from __future__ import annotations

import sys

from agent_learning.fake import FakeChatModel
from agent_learning.llm.chain import ChainService


def main() -> None:
    question = " ".join(sys.argv[1:]) or "How does Chain work?"
    trace = ChainService(FakeChatModel("Chain response.")).ask_with_trace(question)
    print(trace.answer)
    print(f"prompt messages: {len(trace.prompt_messages)}")


if __name__ == "__main__":
    main()
