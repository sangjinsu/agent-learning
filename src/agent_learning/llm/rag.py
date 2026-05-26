from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from langchain_core.messages import BaseMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from agent_learning.llm.prompting import DEFAULT_SYSTEM_PROMPT, is_blank_question

DEFAULT_TOP_K = 2


@dataclass(frozen=True)
class Document:
    id: str
    content: str
    metadata: dict[str, str] = field(default_factory=dict)
    score: float = 0.0


@dataclass(frozen=True)
class Source:
    id: str
    title: str
    source: str
    score: float


@dataclass(frozen=True)
class RAGResult:
    answer: str
    sources: list[Source]
    retrieved_documents: list[Document]
    prompt_messages: list[BaseMessage]
    model_response: BaseMessage


class InMemoryKeywordRetriever:
    def __init__(self, docs: list[Document], default_top_k: int = DEFAULT_TOP_K) -> None:
        self.docs = list(docs)
        self.default_top_k = default_top_k

    def retrieve(self, query: str, top_k: int | None = None) -> list[Document]:
        limit = self.default_top_k if top_k is None else top_k
        if limit <= 0:
            return []
        query_weights = _token_weights(query)
        scored: list[Document] = []
        for doc in self.docs:
            score = _score_document(query_weights, doc)
            if score > 0:
                scored.append(Document(doc.id, doc.content, dict(doc.metadata), float(score)))
        scored.sort(key=lambda doc: (-doc.score, doc.id))
        return scored[:limit]


class RAGService:
    def __init__(self, retriever: InMemoryKeywordRetriever, model, top_k: int = DEFAULT_TOP_K) -> None:
        if retriever is None:
            raise ValueError("rag service: retriever is required")
        if model is None:
            raise ValueError("rag service: model is required")
        self.retriever = retriever
        self.model = model
        self.top_k = top_k
        self.prompt = default_rag_prompt()

    def ask(self, question: str) -> RAGResult:
        return self.ask_with_history(question, [])

    def ask_with_history(self, question: str, history: list[BaseMessage] | None) -> RAGResult:
        if is_blank_question(question):
            raise ValueError("chat service: question must not be blank")
        docs = self.retriever.retrieve(question.strip(), self.top_k)
        if not docs:
            raise ValueError("rag service: no relevant documents found")
        messages = self.prompt.format_messages(question=question.strip(), context=_format_context(docs), history=history or [])
        response = self.model.invoke(messages)
        return RAGResult(
            answer=str(response.content),
            sources=[_source_from_document(doc) for doc in docs],
            retrieved_documents=docs,
            prompt_messages=messages,
            model_response=response,
        )


def default_rag_prompt() -> ChatPromptTemplate:
    return ChatPromptTemplate.from_messages(
        [
            (
                "system",
                DEFAULT_SYSTEM_PROMPT
                + " Answer only from the retrieved context. If the context is insufficient, say so clearly.",
            ),
            MessagesPlaceholder("history", optional=True),
            (
                "human",
                "Use the retrieved context below to answer the question.\n\n"
                "Retrieved context:\n{context}\n\nQuestion: {question}",
            ),
        ]
    )


def load_documents(directory: str | Path) -> list[Document]:
    base = Path(directory)
    docs: list[Document] = []
    for path in sorted(base.iterdir()):
        if path.suffix.lower() not in {".md", ".txt"}:
            continue
        docs.append(
            Document(
                id=path.stem,
                content=path.read_text(encoding="utf-8"),
                metadata={"title": _title_from_file(path), "source": str(path)},
            )
        )
    return docs


def _score_document(query_weights: dict[str, int], doc: Document) -> int:
    doc_weights = _token_weights(f"{doc.id} {doc.metadata.get('title', '')} {doc.content}")
    return sum(weight * doc_weights.get(token, 0) for token, weight in query_weights.items())


def _token_weights(text: str) -> dict[str, int]:
    weights: dict[str, int] = {}
    for token in re.split(r"[^0-9A-Za-z가-힣]+", text.lower()):
        normalized = _normalize_token(token)
        if normalized:
            weights[normalized] = weights.get(normalized, 0) + 1
    return weights


def _normalize_token(token: str) -> str:
    if len(token) <= 2:
        return ""
    if token.endswith("ies") and len(token) > 4:
        return token[:-3] + "y"
    if token.endswith("es") and len(token) > 3:
        return token[:-2]
    if token.endswith("s") and len(token) > 3:
        return token[:-1]
    return token


def _format_context(docs: list[Document]) -> str:
    return "\n\n".join(
        f"[{index}] {doc.metadata.get('title') or doc.id}\nSource: {doc.metadata.get('source', '')}\n{doc.content}"
        for index, doc in enumerate(docs, start=1)
    )


def _source_from_document(doc: Document) -> Source:
    return Source(
        id=doc.id,
        title=doc.metadata.get("title") or doc.id,
        source=doc.metadata.get("source", ""),
        score=doc.score,
    )


def _title_from_file(path: Path) -> str:
    for line in path.read_text(encoding="utf-8").splitlines():
        title = line.strip().lstrip("#").strip()
        if title:
            return title
    return path.stem
