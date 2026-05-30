# Workflow

## Default Verification

외부 API 없이 기본 검증을 실행합니다.

```bash
uv run pytest
uv run python -m compileall -q src examples tests
uv lock --check
```

## Chapter Development Loop

1. 새 behavior를 fake model 또는 local testdata로 먼저 설계합니다.
2. `tests/test_chapters.py`에 behavior test를 추가합니다.
3. `examples/chXX_*.py`에 학습용 CLI trace를 추가합니다.
4. 필요할 때만 `tests/test_openai_integration.py` 또는 `tests/test_provider_integration.py`에 opt-in integration test를 추가합니다.
5. README, `guides/chapters.md`, `guides/chapters/<chapter>.md`, roadmap/progress/notes를 함께 업데이트합니다.

## Integration Verification

실제 provider 호출이 필요할 때만 실행합니다.

```bash
RUN_AGENT_LEARNING_INTEGRATION=1 uv run pytest tests/test_openai_integration.py -v
RUN_AGENT_LEARNING_INTEGRATION=1 AGENT_LEARNING_PROVIDER=anthropic uv run pytest tests/test_provider_integration.py -v
```
