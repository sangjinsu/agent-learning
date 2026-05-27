# Project Guide

## Source Layout

- `src/agent_learning/fake.py`: 외부 API 없는 fake chat/streaming model
- `src/agent_learning/llm/`: chapter별 LangChain/LangGraph service
- `src/agent_learning/tools/`: calculator 같은 local tool
- `src/agent_learning/mcp_demo.py`: local MCP stdio server/client demo
- `examples/`: chapter 실행 entrypoint
- `tests/`: unit, example, opt-in integration tests
- `testdata/docs/ch09-rag`: RAG 예시 문서

## Placement Rules

- 새 학습 단위의 core behavior는 `src/agent_learning/llm/` 또는 명확한 top-level module에 둡니다.
- CLI 관찰 흐름은 `examples/chXX_*.py`에 둡니다.
- 외부 API 없이 검증 가능한 behavior는 `tests/test_chapters.py`에 둡니다.
- 실제 provider 호출은 `tests/test_openai_integration.py`에 opt-in으로 둡니다.
- chapter-facing 설명은 README, `guides/chapters.md`, `docs/learning-roadmap.md`, `docs/progress.md`를 함께 맞춥니다.
