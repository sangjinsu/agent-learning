from __future__ import annotations

import sys

from agent_learning.example_support import (
    print_learning_sections,
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
    print_learning_sections(
        goal="완성된 답변 하나가 아니라 순서대로 도착하는 stream chunk를 모아 final answer를 만드는 흐름을 봅니다.",
        happens=[
            "prompt messages는 일반 chat 호출과 같은 방식으로 만들어집니다.",
            "model.stream()이 AIMessageChunk들을 순서대로 반환합니다.",
            "StreamingService는 빈 chunk를 제외하고 chunk를 이어 붙여 final answer를 만듭니다.",
        ],
        matters="Streaming은 긴 답변의 체감 대기 시간을 줄이고, UI에서 생성 중인 내용을 즉시 보여줄 수 있게 합니다.",
        try_next=[
            "fake chunk 문자열을 더 잘게 나누면 chunk count가 어떻게 바뀌는지 확인해 보세요.",
            "실제 OpenAI mode에서 chunk 개수와 fake mode의 chunk 개수를 비교해 보세요.",
        ],
    )
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
