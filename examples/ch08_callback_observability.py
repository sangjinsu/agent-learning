from __future__ import annotations

import sys

from agent_learning.fake import FakeChatModel
from agent_learning.llm.observability import run_observable_chat_chain


def main() -> None:
    question = " ".join(sys.argv[1:]) or "How do callbacks help?"
    result = run_observable_chat_chain(model=FakeChatModel("Observable response."), question=question)
    print(result.answer)
    for event in result.events:
        print(f"{event.timing} {event.name}: {event.summary}")


if __name__ == "__main__":
    main()
