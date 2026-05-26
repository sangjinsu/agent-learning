from __future__ import annotations

import sys

from agent_learning.fake import FakeChatModel
from agent_learning.llm.graph import GraphInput, GraphService


def main() -> None:
    question = " ".join(sys.argv[1:]) or "calculate: 7 * (8 + 2)"
    result = GraphService(FakeChatModel("Graph chat response.")).run(GraphInput(question=question))
    print(f"route: {result.route}")
    print(result.answer)


if __name__ == "__main__":
    main()
