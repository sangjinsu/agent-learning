from __future__ import annotations

import sys

from agent_learning.fake import FakeStreamingChatModel
from agent_learning.llm.streaming import StreamingService


def main() -> None:
    question = " ".join(sys.argv[1:]) or "How does streaming work?"
    result = StreamingService(FakeStreamingChatModel("Streaming", " response", ".")).ask(question)
    for chunk in result.chunks:
        print(chunk, end="")
    print()


if __name__ == "__main__":
    main()
