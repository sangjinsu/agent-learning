# Progress

이 문서는 현재 완료 상태를 빠르게 확인하기 위한 dashboard입니다. 자세한 목표는 [../guides/chapters.md](../guides/chapters.md), chapter별 상세 문서는 [../guides/chapters/](../guides/chapters/)를 봅니다.

## Status Dashboard

| Chapter | 상태 | 대표 실행 | API key | 빠른 검증 |
| --- | --- | --- | --- | --- |
| 01. ChatModel | 완료 | `uv run python examples/ch01_chatmodel.py "What is LangChain?"` | 불필요 | `uv run pytest tests/test_chapters.py::test_ch01_chat_service_uses_fake_model -q` |
| 02. Prompt Template | 완료 | `uv run python examples/ch02_prompt_template.py "How does ChatPromptTemplate work?"` | 불필요 | `uv run pytest tests/test_chapters.py::test_ch02_prompt_formats_system_history_and_question -q` |
| 03. Provider ChatModel | 완료 | `uv run python examples/ch03_openai_chatmodel.py "What does provider ChatModel do?"` | 선택 | `uv run pytest tests/test_chapters.py::test_ch03_example_is_opt_in_and_safe_without_api_key -q` |
| 04. Tool Calling | 완료 | `uv run python examples/ch04_tool_calling.py "12 * (7 + 3)"` | 선택 | `uv run pytest tests/test_chapters.py::test_ch04_tool_calling_executes_calculator_loop -q` |
| 05. Chain | 완료 | `uv run python examples/ch05_chain.py "How does Chain work?"` | 선택 | `uv run pytest tests/test_chapters.py::test_ch05_chain_service_runs_prompt_model_chain_with_trace -q` |
| 06. Graph | 완료 | `uv run python examples/ch06_graph.py "calculate: 7 * (8 + 2)"` | 선택 | `uv run pytest tests/test_chapters.py::test_ch06_graph_routes_calculation_without_model_call_and_chat_with_model_call -q` |
| 07. Streaming | 완료 | `uv run python examples/ch07_streaming.py "How does streaming work?"` | 선택 | `uv run pytest tests/test_chapters.py::test_ch07_streaming_collects_chunks -q` |
| 08. Callback | 완료 | `uv run python examples/ch08_callback_observability.py "How do callbacks help?"` | 선택 | `uv run pytest tests/test_chapters.py::test_ch08_observability_records_chain_events -q` |
| 09. RAG | 완료 | `uv run python examples/ch09_rag.py "Chapter 8 callback은 RAG에서 어떤 흐름을 관찰하나요?"` | 선택 | `uv run pytest tests/test_chapters.py::test_ch09_rag_retrieves_keyword_context_and_sources -q` |
| 10. MCP | 완료 | `uv run python examples/ch10_mcp.py tool` | 불필요 | `uv run pytest tests/test_chapters.py::test_ch10_mcp_demo_supports_focused_flows -q` |
| 11. ReAct Agent | 완료 | `uv run python examples/ch11_react_agent.py "12 * (7 + 3)"` | 선택 | `uv run pytest tests/test_chapters.py::test_ch11_react_agent_runs_reason_action_observation_loop -q` |
| 12. GraphTool | 완료 | `uv run python examples/ch12_graphtool.py "triage checkout 500 errors increased in prod"` | 선택 | `uv run pytest tests/test_chapters.py::test_ch12_graphtool_react_agent_calls_devops_triage_graph -q` |

## 공통 검증

외부 API 없이 전체 테스트를 실행합니다.

```bash
uv run pytest -q
uv run python -m compileall -q src examples tests
uv lock --check
```

Markdown과 diff whitespace를 확인합니다.

```bash
git diff --check
```

실제 provider 동작은 필요할 때만 opt-in으로 확인합니다.

```bash
RUN_AGENT_LEARNING_INTEGRATION=1 uv run pytest tests/test_openai_integration.py -v
RUN_AGENT_LEARNING_INTEGRATION=1 AGENT_LEARNING_PROVIDER=anthropic uv run pytest tests/test_provider_integration.py -v
```

## Output Policy

- 기본 예제 출력은 결과 중심으로 짧게 유지합니다.
- 상세 학습 trace는 `--verbose`를 붙여 확인합니다.
- 기본 `uv run pytest`는 외부 API를 호출하지 않습니다.
