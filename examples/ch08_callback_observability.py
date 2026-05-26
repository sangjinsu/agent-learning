from __future__ import annotations

import sys

from agent_learning.example_support import print_model_selection, select_chat_model
from agent_learning.llm.observability import run_observable_chat_chain


def main() -> None:
    question = " ".join(sys.argv[1:]) or "How do callbacks help?"
    selection = select_chat_model("Observable response from chapter 08.")
    result = run_observable_chat_chain(model=selection.model, question=question)

    print_model_selection(selection)
    print(f"question: {question}")
    print("callback events:")
    for index, event in enumerate(result.events):
        print(f"- [{index}] {event.timing} {event.name} ({event.component}): {event.summary}")
    if not result.events:
        print("- none")
    print(f"final answer: {result.answer}")


if __name__ == "__main__":
    main()
