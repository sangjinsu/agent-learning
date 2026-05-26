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


_STOPWORDS = {"chapter", "does", "what", "when", "where", "which", "with", "from", "into", "about", "어떤"}
_KOREAN_SUFFIXES = ("하나요", "인가요", "에서", "으로", "에게", "에는", "부터", "까지", "은", "는", "이", "가", "을", "를", "로", "에", "과", "와", "요")
_TOKEN_ALIASES = {
    "callback": ("observability", "event", "events"),
    "관찰": ("observability", "record", "records", "event", "events"),
    "흐름": ("flow", "pipeline", "lifecycle"),
    "rag": ("retrieval", "retrieve", "retrieved", "context", "source", "sources"),
}


def _token_weights(text: str) -> dict[str, int]:
    weights: dict[str, int] = {}
    for raw_token in re.split(r"[^0-9A-Za-z가-힣]+", text.lower()):
        for token in _expand_raw_token(raw_token):
            weights[token] = weights.get(token, 0) + 1
    return weights


def _expand_raw_token(raw_token: str) -> list[str]:
    expanded: list[str] = []
    normalized = _normalize_token(raw_token)
    if normalized:
        expanded.extend(_expand_normalized_token(normalized))

    match = re.fullmatch(r"([a-z]+)(\d+)", raw_token)
    if match:
        expanded.extend(_expand_normalized_token(match.group(2)))

    return list(dict.fromkeys(expanded))


def _expand_normalized_token(token: str) -> list[str]:
    if token in _STOPWORDS:
        return []
    tokens = [token]
    if token.isdigit():
        number = int(token)
        tokens.extend([str(number), f"{number:02d}"])
    tokens.extend(_TOKEN_ALIASES.get(token, ()))
    return list(dict.fromkeys(item for item in tokens if item and item not in _STOPWORDS))


def _normalize_token(token: str) -> str:
    if not token:
        return ""
    if token.isdigit():
        return str(int(token))
    token = _strip_korean_suffix(token)
    if len(token) <= 2:
        return ""
    if token.endswith("ies") and len(token) > 4:
        return token[:-3] + "y"
    if token.endswith("es") and len(token) > 3:
        return token[:-2]
    if token.endswith("s") and len(token) > 3:
        return token[:-1]
    return token


def _strip_korean_suffix(token: str) -> str:
    for suffix in _KOREAN_SUFFIXES:
        if token.endswith(suffix) and len(token) > len(suffix) + 1:
            return token[: -len(suffix)]
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
