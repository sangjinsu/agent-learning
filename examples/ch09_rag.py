from __future__ import annotations

import sys
from pathlib import Path

from agent_learning.example_support import (
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
