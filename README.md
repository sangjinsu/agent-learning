# agent-learning

Python LangGraph/LangChain으로 agent 학습 흐름을 단계별로 익히는 저장소입니다. `../eino-learning`의 Chapter 01-09 구성을 Python 생태계에 맞춰 복제했습니다.

초반 chapter는 외부 API 없이 fake model로 구조와 테스트를 먼저 익히고, 실제 OpenAI 호출은 `RUN_AGENT_LEARNING_INTEGRATION=1`일 때만 opt-in으로 다룹니다.

## Setup

```bash
uv sync
uv run pytest
```

## Chapters

- Chapter 01: `ChatService`와 `FakeChatModel`
- Chapter 02: `ChatPromptTemplate` 기반 system/history/question prompt formatting
- Chapter 03: `.env`/환경 변수 기반 `ChatOpenAI` factory
- Chapter 04: `bind_tools` 기반 calculator tool calling loop
- Chapter 05: `ChatPromptTemplate | model` runnable chain
- Chapter 06: LangGraph `StateGraph` routing
- Chapter 07: streaming chunk 수집
- Chapter 08: callback-style observability recorder
- Chapter 09: keyword 기반 in-memory RAG

## Examples

```bash
uv run python examples/ch01_chatmodel.py "What is LangChain?"
uv run python examples/ch04_tool_calling.py "12 * (7 + 3)"
uv run python examples/ch06_graph.py "calculate: 7 * (8 + 2)"
uv run python examples/ch09_rag.py "How does RAG cite sources?"
```

## Integration

```env
OPENAI_API_KEY=your-api-key
OPENAI_MODEL=gpt-4.1-mini
OPENAI_BASE_URL=
RUN_AGENT_LEARNING_INTEGRATION=1
```

기본 `uv run pytest`는 외부 API를 호출하지 않습니다.

실제 OpenAI 연동 확인은 명시적으로 opt-in합니다.

```bash
RUN_AGENT_LEARNING_INTEGRATION=1 uv run pytest tests/test_openai_integration.py -v
```

`OPENAI_API_KEY`가 없으면 integration tests는 skip됩니다.
