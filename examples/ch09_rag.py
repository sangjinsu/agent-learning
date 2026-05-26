from __future__ import annotations

import sys
from pathlib import Path

from agent_learning.example_support import (
    print_learning_sections,
    print_messages,
    print_model_selection,
    select_chat_model,
)
from agent_learning.llm.rag import InMemoryKeywordRetriever, RAGService, load_documents


def main() -> None:
    question = " ".join(sys.argv[1:]) or "How does RAG cite sources?"
    docs_dir = Path(__file__).resolve().parents[1] / "testdata/docs/ch09-rag"
    docs = load_documents(docs_dir)
    selection = select_chat_model("RAG response from retrieved context.")
    result = RAGService(InMemoryKeywordRetriever(docs), selection.model).ask(question)

    print_model_selection(selection)
    print_learning_sections(
        goal="질문과 관련된 문서를 먼저 검색하고, 검색된 context만 prompt에 넣어 답변하는 RAG 기본 흐름을 봅니다.",
        happens=[
            "load_documents()가 local markdown/text 파일을 Document와 metadata로 바꿉니다.",
            "InMemoryKeywordRetriever가 query token과 document token의 overlap으로 source를 고릅니다.",
            "RAG prompt는 retrieved context, source metadata, question을 함께 model에 전달합니다.",
        ],
        matters="RAG는 model의 기억에만 의존하지 않고 어떤 문서를 근거로 답했는지 sources와 함께 확인하게 해 줍니다.",
        try_next=[
            'callback 질문: uv run python examples/ch09_rag.py "Chapter 8 callback은 RAG에서 어떤 흐름을 관찰하나요?"',
            'tool calling 질문: uv run python examples/ch09_rag.py "tool calling calculator schema safe arithmetic"',
            'streaming 질문: uv run python examples/ch09_rag.py "streaming chunk final answer user interface"',
            "retrieved sources의 score를 보며 어떤 문서가 선택되는지 확인해 보세요.",
        ],
    )
    print(f"question: {question}")
    print("loaded documents:")
    for doc in docs:
        print(f"- {doc.metadata.get('title', doc.id)}: {doc.metadata.get('source', '')}")
    if not docs:
        print("- none")
    print("retrieved sources:")
    for source in result.sources:
        print(f"- score={source.score:.2f} {source.title}: {source.source}")
    if not result.sources:
        print("- none")
    print("prompt context summary:")
    print(f"- retrieved_document_count: {len(result.retrieved_documents)}")
    print("- retrieved_document_ids: " + ", ".join(doc.id for doc in result.retrieved_documents))
    print(f"- prompt_message_count: {len(result.prompt_messages)}")
    print_messages("prompt messages", result.prompt_messages)
    print(f"final answer: {result.answer}")


if __name__ == "__main__":
    main()
