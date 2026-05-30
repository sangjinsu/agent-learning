# agent-learning

Python, LangChain, LangGraph로 agent 애플리케이션의 기본 구성 요소를 단계별로 익히는 학습 저장소입니다.

각 chapter는 실행 가능한 CLI 예제와 pytest를 함께 제공합니다. 기본 실행은 fake model과 local testdata를 사용하므로 외부 LLM API를 호출하지 않습니다. 실제 OpenAI 호출은 `RUN_AGENT_LEARNING_INTEGRATION=1`을 명시했을 때만 opt-in으로 실행합니다.

## Quick Start

요구 사항:

- Python 3.11 이상
- `uv`
- 실제 OpenAI integration 실행 시 `OPENAI_API_KEY`

설치와 기본 검증:

```bash
uv sync
uv run pytest
```

기본 `uv run pytest`는 외부 API를 호출하지 않습니다. `OPENAI_API_KEY`가 없으면 integration tests는 skip됩니다.

실제 OpenAI 연동 테스트:

```bash
RUN_AGENT_LEARNING_INTEGRATION=1 uv run pytest tests/test_openai_integration.py -v
```

## Quick Run Examples

전체 흐름을 빠르게 훑고 싶다면 아래 명령을 순서대로 실행합니다.

```bash
uv run python examples/ch01_chatmodel.py "What is LangChain?"
uv run python examples/ch02_prompt_template.py "How does ChatPromptTemplate work?"
uv run python examples/ch03_openai_chatmodel.py "What does ChatOpenAI do?"
uv run python examples/ch04_tool_calling.py "12 * (7 + 3)"
uv run python examples/ch05_chain.py "How does Chain work?"
uv run python examples/ch06_graph.py
uv run python examples/ch06_graph.py "calculate: 7 * (8 + 2)"
uv run python examples/ch07_streaming.py "How does streaming work?"
uv run python examples/ch08_callback_observability.py "callback observability는 무엇을 관찰하나요?"
uv run python examples/ch09_rag.py "Chapter 8 callback은 RAG에서 어떤 흐름을 관찰하나요?"
uv run python examples/ch09_rag.py "tool calling calculator schema safe arithmetic"
uv run python examples/ch09_rag.py "streaming chunk final answer user interface"
uv run python examples/ch10_mcp.py discover
uv run python examples/ch10_mcp.py resource
uv run python examples/ch10_mcp.py prompt
uv run python examples/ch10_mcp.py tool
uv run python examples/ch10_mcp.py full
uv run python examples/ch11_react_agent.py "12 * (7 + 3)"
```

## Learning Map

| Chapter | Topic | 관찰할 흐름 |
| --- | --- | --- |
| 01 | ChatModel | fake model로 질문/응답 service 경계를 만듭니다. |
| 02 | Prompt Template | system/history/user message 순서를 고정합니다. |
| 03 | OpenAI ChatModel | `.env` 기반 provider 설정과 opt-in integration을 분리합니다. |
| 04 | Tool Calling | model tool call을 allowlist 기반 local tool execution으로 연결합니다. |
| 05 | Chain | `ChatPromptTemplate | model` runnable pipeline을 구성합니다. |
| 06 | Graph | LangGraph로 calculator/chat branch를 routing합니다. |
| 07 | Streaming | stream chunk를 순서대로 수집해 final answer로 합칩니다. |
| 08 | Callback / Observability | prompt/model lifecycle event를 recorder로 관찰합니다. |
| 09 | RAG | local 문서 검색, context prompt, source metadata를 연결합니다. |
| 10 | MCP | FastMCP server와 stdio client로 tool/resource/prompt를 호출합니다. |
| 11 | ReAct Agent | reasoning/action/observation loop를 LangGraph로 실행합니다. |

자세한 chapter별 목표, 핵심 개념, 실행 명령, 테스트 명령은 [Chapter Guide](guides/chapters.md)에서 원하는 chapter 문서로 이동해 확인합니다.

## Project Structure

```text
examples/                 # chapter별 CLI entrypoint
src/agent_learning/
  fake.py                 # 외부 API 없는 fake chat/streaming model
  mcp_demo.py             # local MCP stdio server/client demo
  llm/                    # chapter별 LangChain/LangGraph service
  tools/                  # calculator 같은 local tool
tests/                    # unit, example, opt-in integration tests
testdata/docs/ch09-rag/   # RAG용 local 문서
```

핵심 구성 요소:

- Chat model: `invoke()`와 `stream()`을 통해 답변 또는 chunk를 반환합니다.
- Prompt template: `ChatPromptTemplate`으로 system/history/user message를 구성합니다.
- Tool calling: `bind_tools()`와 allowlist 기반 tool execution loop를 사용합니다.
- Graph: LangGraph `StateGraph`로 route, calculator, prompt, model node를 연결합니다.
- Retriever: `InMemoryKeywordRetriever`가 local 문서를 검색하고 source metadata를 유지합니다.
- MCP: `FastMCP` server와 stdio client session으로 tool/resource/prompt를 노출하고 호출합니다.
- ReAct Agent: LangGraph loop로 reasoning, action, observation, final answer를 연결합니다.

## CLI Trace

모든 chapter 예제는 단순한 답변 한 줄 대신 학습용 trace를 출력합니다.

- `mode:`: fake/local/integration 실행 모드
- `learning goal:` / `학습 목표:`: chapter에서 관찰할 핵심 목표
- `what happens:` / `실행 흐름:`: 입력이 component를 지나며 바뀌는 단계
- `why it matters:` / `중요한 이유:`: 실제 agent 애플리케이션에서 중요한 이유
- `try next:` / `다음 실습:`: 같은 예제를 변형해 볼 수 있는 실습

그 뒤에는 chapter 성격에 따라 prompt messages, tool calls, graph route, stream chunks, callback events, retrieved sources, MCP call trace, ReAct steps, final answer를 단계별로 출력합니다.

## Environment

`.env` 예시:

```env
OPENAI_API_KEY=your-api-key
OPENAI_MODEL=gpt-4.1-mini
OPENAI_BASE_URL=
RUN_AGENT_LEARNING_INTEGRATION=0
```

실제 OpenAI 호출을 실행할 때만 `RUN_AGENT_LEARNING_INTEGRATION=1`로 바꿉니다.

설정 우선순위:

1. Shell 환경 변수
2. repository root의 `.env`
3. 코드 기본값

기본 모델명은 `gpt-4.1-mini`입니다.

## Verification

외부 API 없이 전체 검증:

```bash
uv run pytest
uv run python -m compileall -q src examples tests
uv lock --check
```

실제 OpenAI integration 검증:

```bash
RUN_AGENT_LEARNING_INTEGRATION=1 uv run pytest tests/test_openai_integration.py -v
```

## Documentation

- [Chapter Guide](guides/chapters.md): chapter별 상세 문서 인덱스
- [Chapter Details](guides/chapters/): Chapter 01-11 상세 학습 목표, 실행 명령, 테스트 명령
- [Learning Roadmap](docs/learning-roadmap.md): 학습 순서와 다음 확장 후보
- [Project Guide](guides/project.md): 소스 구조와 파일 배치 기준
- [Workflow](guides/workflow.md): 개발/검증 루프
- [Security Guide](guides/security.md): tool, API key, integration safety 기준
- [Notes](docs/notes.md): 구현 중 유지해야 하는 설계 메모

## Current Coverage

- Chapter 03-09 OpenAI integration tests는 opt-in입니다.
- Chapter 09는 embedding/vector store 없이 in-memory keyword retrieval만 다룹니다.
- Chapter 10은 배포용 remote connector가 아니라 local stdio MCP 학습 예제입니다.
- Chapter 11은 실제 OpenAI agent가 아니라 fake model과 calculator tool로 보는 local ReAct 학습 예제입니다.
