from __future__ import annotations

import sys
from pathlib import Path

from agent_learning.fake import FakeChatModel
from agent_learning.llm.rag import InMemoryKeywordRetriever, RAGService, load_documents


def main() -> None:
    question = " ".join(sys.argv[1:]) or "How does RAG cite sources?"
    docs = load_documents(Path(__file__).resolve().parents[1] / "testdata/docs/ch09-rag")
    result = RAGService(InMemoryKeywordRetriever(docs), FakeChatModel("RAG response from retrieved context.")).ask(question)
    print(result.answer)
    for source in result.sources:
        print(f"- {source.title}: {source.source}")


if __name__ == "__main__":
    main()
