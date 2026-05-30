# Chapter 04. Tool Calling

## 목표

- LangChain tool metadata와 실제 tool 실행 경계를 이해합니다.
- `model.bind_tools()`로 model에게 tool schema를 전달합니다.
- model이 생성한 `tool_calls`를 allowlist 기반으로 실행해 `ToolMessage`를 만듭니다.
- tool 결과를 message history에 붙여 model에게 최종 답변을 다시 요청합니다.

## 핵심 개념

- tool은 model에게 보여줄 schema와 실제 실행 함수가 함께 있어야 합니다.
- 이번 장의 `calculator` tool은 `+`, `-`, `*`, `/`, 괄호만 지원하는 안전한 실제 계산 tool입니다.
- `ToolCallingService`는 `model -> tool calls -> ToolMessage -> model final answer` loop를 실행합니다.
- 초반 chapter에서는 shell, 파일 삭제, 배포 같은 위험 tool을 등록하지 않습니다.
- Python AST whitelist에서 `True` 같은 bool literal과 함수 호출은 거부합니다.

## 실행 명령

```bash
uv run python examples/ch04_tool_calling.py "12 * (7 + 3)"
```

## 확인할 출력/테스트

CLI에서 확인할 부분:

- `tool schemas`에 calculator schema가 노출되는지 확인합니다.
- `tool messages`에 calculator 실행 결과가 `ToolMessage`로 추가되는지 확인합니다.
- `final answer`가 tool 결과를 보고 생성되는지 확인합니다.

테스트:

```bash
uv run pytest tests/test_chapters.py::test_ch04_calculator_supports_safe_arithmetic_and_rejects_calls -q
uv run pytest tests/test_chapters.py::test_ch04_tool_calling_executes_calculator_loop -q
RUN_AGENT_LEARNING_INTEGRATION=1 uv run pytest tests/test_openai_integration.py::test_openai_tool_calling_integration -v
```
