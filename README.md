# agent-learning

Python, LangChain, LangGraph로 agent 애플리케이션의 기본 구성 요소를 단계별로 익히는 학습 저장소입니다.

각 chapter는 실행 가능한 CLI 예제와 pytest를 함께 제공합니다. 기본 실행은 fake model과 local testdata를 사용하므로 외부 LLM API를 호출하지 않습니다. 실제 OpenAI 또는 Anthropic 호출은 `RUN_AGENT_LEARNING_INTEGRATION=1`을 명시했을 때만 opt-in으로 실행합니다.

## Quick Start

요구 사항:

- Python 3.11 이상
- `uv`
- 실제 OpenAI integration 실행 시 `OPENAI_API_KEY`
- 실제 Anthropic integration 실행 시 `ANTHROPIC_API_KEY`

설치와 기본 검증:

```bash
uv sync
uv run pytest
```

기본 `uv run pytest`는 외부 API를 호출하지 않습니다. provider API key가 없으면 integration tests는 skip됩니다.

실제 provider 연동 테스트:

```bash
RUN_AGENT_LEARNING_INTEGRATION=1 uv run pytest tests/test_openai_integration.py -v
RUN_AGENT_LEARNING_INTEGRATION=1 AGENT_LEARNING_PROVIDER=anthropic uv run pytest tests/test_provider_integration.py -v
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
uv run python examples/ch12_graphtool.py "triage checkout 500 errors increased in prod"
uv run python examples/ch13_human_in_loop.py "triage checkout 500 errors increased in prod"
```

Chapter 11-12 agent 예제를 실제 모델로 실행하려면 integration flag와 provider key를 함께 설정합니다.

```bash
RUN_AGENT_LEARNING_INTEGRATION=1 AGENT_LEARNING_PROVIDER=openai uv run python examples/ch11_react_agent.py "12 * (7 + 3)"
RUN_AGENT_LEARNING_INTEGRATION=1 AGENT_LEARNING_PROVIDER=anthropic uv run python examples/ch11_react_agent.py "12 * (7 + 3)"
RUN_AGENT_LEARNING_INTEGRATION=1 AGENT_LEARNING_PROVIDER=openai uv run python examples/ch12_graphtool.py "triage checkout 500 errors increased in prod"
RUN_AGENT_LEARNING_INTEGRATION=1 AGENT_LEARNING_PROVIDER=anthropic uv run python examples/ch12_graphtool.py "triage checkout 500 errors increased in prod"
```

## Learning Map

| Chapter | Topic | 관찰할 흐름 |
| --- | --- | --- |
| 01 | ChatModel | fake model로 질문/응답 service 경계를 만듭니다. |
| 02 | Prompt Template | system/history/user message 순서를 고정합니다. |
| 03 | Provider ChatModel | `.env` 기반 provider 설정과 opt-in integration을 분리합니다. |
| 04 | Tool Calling | model tool call을 allowlist 기반 local tool execution으로 연결합니다. |
| 05 | Chain | `ChatPromptTemplate | model` runnable pipeline을 구성합니다. |
| 06 | Graph | LangGraph로 calculator/chat branch를 routing합니다. |
| 07 | Streaming | stream chunk를 순서대로 수집해 final answer로 합칩니다. |
| 08 | Callback / Observability | prompt/model lifecycle event를 recorder로 관찰합니다. |
| 09 | RAG | local 문서 검색, context prompt, source metadata를 연결합니다. |
| 10 | MCP | FastMCP server와 stdio client로 tool/resource/prompt를 호출합니다. |
| 11 | ReAct Agent | reasoning/action/observation loop를 LangGraph로 실행합니다. |
| 12 | GraphTool | DevOps triage LangGraph를 tool로 감싸 ReAct Agent가 호출합니다. |
| 13 | Human-in-the-loop | incident action 실행 전 interrupt approval gate를 둡니다. |

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
- Provider selection: `AGENT_LEARNING_PROVIDER=openai|anthropic`으로 실제 model provider를 선택합니다.
- Prompt template: `ChatPromptTemplate`으로 system/history/user message를 구성합니다.
- Tool calling: `bind_tools()`와 allowlist 기반 tool execution loop를 사용합니다.
- Graph: LangGraph `StateGraph`로 route, calculator, prompt, model node를 연결합니다.
- Retriever: `InMemoryKeywordRetriever`가 local 문서를 검색하고 source metadata를 유지합니다.
- MCP: `FastMCP` server와 stdio client session으로 tool/resource/prompt를 노출하고 호출합니다.
- ReAct Agent: LangGraph loop로 reasoning, action, observation, final answer를 연결합니다.
- GraphTool: deterministic LangGraph workflow를 `StructuredTool`로 감싸 agent action으로 호출합니다.
- Human-in-the-loop: LangGraph `interrupt`와 `Command(resume=...)`로 action 전 approval gate를 관찰합니다.

## CLI Output

모든 chapter 예제는 기본적으로 결과 중심의 짧은 출력을 보여줍니다.

- 첫 줄: chapter 성격을 나타내는 짧은 label. 예: `rag:`, `mcp demo:`, `react agent:`
- `mode:`: fake/local/provider 실행 모드
- 핵심 결과: retrieved sources, selected route, tool result, step summary 같은 chapter별 요약
- `final answer:`: 최종 응답 또는 완료 결과

상세 학습 trace가 필요하면 `--verbose`를 붙입니다.

```bash
uv run python examples/ch09_rag.py --verbose "Chapter 8 callback은 RAG에서 어떤 흐름을 관찰하나요?"
uv run python examples/ch11_react_agent.py --verbose "12 * (7 + 3)"
uv run python examples/ch12_graphtool.py --verbose "triage checkout 500 errors increased in prod"
uv run python examples/ch13_human_in_loop.py --verbose "triage checkout 500 errors increased in prod"
```

`--verbose` 출력에는 learning goal, 실행 흐름, prompt messages, tool calls, graph route, stream chunks, callback events, MCP call trace, ReAct steps, GraphTool observation, HITL interrupt/resume trace가 포함됩니다.

## Environment

`.env` 예시:

```env
OPENAI_API_KEY=your-api-key
OPENAI_MODEL=gpt-4.1-mini
OPENAI_BASE_URL=
AGENT_LEARNING_PROVIDER=openai
ANTHROPIC_API_KEY=your-anthropic-api-key
ANTHROPIC_MODEL=claude-sonnet-4-6
RUN_AGENT_LEARNING_INTEGRATION=0
```

실제 provider 호출을 실행할 때만 `RUN_AGENT_LEARNING_INTEGRATION=1`로 바꿉니다.

설정 우선순위:

1. Shell 환경 변수
2. repository root의 `.env`
3. 코드 기본값

기본 provider는 `openai`입니다. 기본 모델명은 OpenAI `gpt-4.1-mini`, Anthropic `claude-sonnet-4-6`입니다.

## Verification

외부 API 없이 전체 검증:

```bash
uv run pytest
uv run python -m compileall -q src examples tests
uv lock --check
```

실제 provider integration 검증:

```bash
RUN_AGENT_LEARNING_INTEGRATION=1 uv run pytest tests/test_openai_integration.py -v
RUN_AGENT_LEARNING_INTEGRATION=1 AGENT_LEARNING_PROVIDER=anthropic uv run pytest tests/test_provider_integration.py -v
```

## Documentation

- [Chapter Guide](guides/chapters.md): chapter별 상세 문서 인덱스
- [Chapter Details](guides/chapters/): Chapter 01-13 상세 학습 목표, 실행 명령, 테스트 명령
- [Learning Roadmap](docs/learning-roadmap.md): 학습 순서와 다음 확장 후보
- [Project Guide](guides/project.md): 소스 구조와 파일 배치 기준
- [Workflow](guides/workflow.md): 개발/검증 루프
- [Security Guide](guides/security.md): tool, API key, integration safety 기준
- [Notes](docs/notes.md): 구현 중 유지해야 하는 설계 메모

## Current Coverage

- Chapter 03-09 OpenAI integration tests는 opt-in입니다.
- Chapter 09는 embedding/vector store 없이 in-memory keyword retrieval만 다룹니다.
- Chapter 10은 배포용 remote connector가 아니라 local stdio MCP 학습 예제입니다.
- Chapter 11은 fake mode가 기본이며, opt-in으로 OpenAI 또는 Anthropic 실제 모델 ReAct 예시를 실행할 수 있습니다.
- Chapter 12는 fake mode가 기본이며, DevOps triage graph를 ReAct Agent의 tool action으로 호출합니다.
- Chapter 13은 local HITL approval gate이며, incident decision만 기록하고 production action은 실행하지 않습니다.
