from __future__ import annotations

import sys

from agent_learning.example_support import (
    print_messages,
    print_model_selection,
    select_streaming_model,
)
from agent_learning.llm.streaming import StreamingService


def main() -> None:
    question = " ".join(sys.argv[1:]) or "How does streaming work?"
    selection = select_streaming_model("Streaming", " response", " from chapter 07.")
    result = StreamingService(selection.model).ask(question)

    print_model_selection(selection)
    print(f"question: {question}")
    print_messages("prompt messages", result.prompt_messages)
    print("stream chunks:")
    for index, chunk in enumerate(result.chunks):
        print(f"- [{index}] {chunk}")
    if not result.chunks:
        print("- none")
    print(f"chunk count: {len(result.chunks)}")
    print(f"final answer: {result.answer}")


if __name__ == "__main__":
    main()
