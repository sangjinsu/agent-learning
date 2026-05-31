# Chapter Guide

이 문서는 chapter별 상세 튜토리얼로 들어가는 인덱스입니다. 각 chapter의 목표, 핵심 개념, 실행 명령, 확인할 출력/테스트는 `guides/chapters/` 아래 개별 문서에서 확인합니다.

각 chapter는 `examples/chXX_*.py`에서 실행 흐름을 확인하고, `tests/test_chapters.py`에서 외부 API 없는 behavior를 검증합니다.

## 공통 규칙

- 기본 실행은 fake model 또는 local testdata만 사용합니다.
- 실제 provider 연동은 `RUN_AGENT_LEARNING_INTEGRATION=1`일 때만 실행합니다.
- 예제 CLI 기본 출력은 `mode:`와 핵심 결과만 짧게 보여주고, 상세 학습 trace는 `--verbose`에서 출력합니다.
- 새 chapter를 추가할 때는 code, example, tests, README, guides, docs를 같은 작업 단위에서 맞춥니다.

## Concept Mapping

Go판 Eino component 개념은 Python에서 다음처럼 대응합니다.

| Eino 개념 | Python 구현 |
| --- | --- |
| `ChatModel` | LangChain chat model `invoke` / `stream` |
| `ChatTemplate` | `ChatPromptTemplate` |
| `WithTools` | `bind_tools` |
| `ToolsNode` | local `ToolMessage` execution loop |
| `Graph` | LangGraph `StateGraph` |
| `Retriever` | `InMemoryKeywordRetriever` |
| `MCP server` | `FastMCP` + `ClientSession` stdio demo |
| `Agent` | LangGraph `llm_call -> tool_node -> llm_call` ReAct loop |
| `GraphTool` | LangGraph subgraph wrapped as a LangChain `StructuredTool` |

## Chapter Index

| Chapter | Topic | Detail | Example | Primary unit test |
| --- | --- | --- | --- | --- |
| 01 | ChatModel | [01-chatmodel.md](chapters/01-chatmodel.md) | `examples/ch01_chatmodel.py` | `test_ch01_chat_service_uses_fake_model` |
| 02 | Prompt Template | [02-prompt-template.md](chapters/02-prompt-template.md) | `examples/ch02_prompt_template.py` | `test_ch02_prompt_formats_system_history_and_question` |
| 03 | Provider ChatModel | [03-openai-chatmodel.md](chapters/03-openai-chatmodel.md) | `examples/ch03_openai_chatmodel.py` | `test_ch03_config_prefers_environment_and_disables_integration_by_default` |
| 04 | Tool Calling | [04-tool-calling.md](chapters/04-tool-calling.md) | `examples/ch04_tool_calling.py` | `test_ch04_tool_calling_executes_calculator_loop` |
| 05 | Chain | [05-chain.md](chapters/05-chain.md) | `examples/ch05_chain.py` | `test_ch05_chain_service_runs_prompt_model_chain_with_trace` |
| 06 | Graph | [06-graph.md](chapters/06-graph.md) | `examples/ch06_graph.py` | `test_ch06_graph_routes_calculation_without_model_call_and_chat_with_model_call` |
| 07 | Streaming | [07-streaming.md](chapters/07-streaming.md) | `examples/ch07_streaming.py` | `test_ch07_streaming_collects_chunks` |
| 08 | Callback / Observability | [08-callback-observability.md](chapters/08-callback-observability.md) | `examples/ch08_callback_observability.py` | `test_ch08_observability_records_chain_events` |
| 09 | RAG | [09-rag.md](chapters/09-rag.md) | `examples/ch09_rag.py` | `test_ch09_rag_retrieves_keyword_context_and_sources` |
| 10 | MCP | [10-mcp.md](chapters/10-mcp.md) | `examples/ch10_mcp.py` | `test_ch10_mcp_demo_exposes_tool_resource_and_prompt_over_stdio` |
| 11 | ReAct Agent | [11-react-agent.md](chapters/11-react-agent.md) | `examples/ch11_react_agent.py` | `test_ch11_react_agent_runs_reason_action_observation_loop` |
| 12 | GraphTool | [12-graphtool.md](chapters/12-graphtool.md) | `examples/ch12_graphtool.py` | `test_ch12_graphtool_react_agent_calls_devops_triage_graph` |

## Integration Coverage

- Chapter 03: `ChatOpenAI` / `ChatAnthropic` provider factory와 `ChatService`
- Chapter 04: `bind_tools` 기반 calculator tool calling
- Chapter 05: runnable chain과 history prompt
- Chapter 06: LangGraph calculator/chat routing
- Chapter 07: streaming chunk collection
- Chapter 08: observable chain event recording
- Chapter 09: keyword RAG, context prompt, source metadata
- Chapter 10: local MCP stdio server/client, tool/resource/prompt
- Chapter 11: local ReAct loop with calculator action and tool observation
- Chapter 12: DevOps triage LangGraph wrapped as a ReAct Agent tool action
