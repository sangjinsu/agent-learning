from __future__ import annotations

import sys

from agent_learning.fake import FakeChatModel
from agent_learning.llm.toolcalling import ToolCallingService
from agent_learning.tools.calculator import calculator_tool


def main() -> None:
    question = " ".join(sys.argv[1:]) or "12 * (7 + 3)"
    result = ToolCallingService(FakeChatModel()).ask(question, [calculator_tool()])
    print(result.answer)


if __name__ == "__main__":
    main()
