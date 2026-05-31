# Agent Instructions

- 모든 보고는 한국어로 합니다.
- 코드 주석은 영어로 유지합니다.
- 이 저장소는 Python 3.11+, `uv`, LangChain, LangGraph, MCP 기반의 Chapter 01-12 학습 저장소입니다.

## Safety

- `uv run pytest`는 외부 API 없이 통과해야 합니다.
- 실제 OpenAI 또는 Anthropic 호출은 `RUN_AGENT_LEARNING_INTEGRATION=1`일 때만 실행합니다.
- provider 선택은 `AGENT_LEARNING_PROVIDER=openai|anthropic`을 사용합니다.
- `.env`는 commit하지 않고, API key와 provider 설정은 `.env.example` 기준으로 맞춥니다.
- `OPENAI_API_KEY`와 `ANTHROPIC_API_KEY` 값을 출력하지 않습니다.

## Example Policy

- `examples/ch01_*.py`부터 `examples/ch12_*.py`까지의 기본 출력은 결과 중심으로 짧게 유지합니다.
- 상세 학습 trace가 필요할 때만 `--verbose`를 사용합니다.
- Chapter 09 RAG는 `testdata/docs/ch09-rag`의 local 문서만 읽습니다.
- Chapter 10 MCP는 local stdio demo이며 remote connector나 production deployment를 다루지 않습니다.
- Chapter 11 ReAct Agent는 calculator tool만 사용하며 shell/filesystem/deployment action은 추가하지 않습니다.
- Chapter 12 GraphTool은 DevOps triage 권고만 생성하며 실제 paging/rollback/deployment action은 추가하지 않습니다.

## Docs and Chapters

- chapter 관련 변경은 example, tests, README, `guides/chapters.md`, 해당 chapter 문서를 함께 맞춥니다.
- 상태 확인은 `docs/progress.md`를 먼저 보고, 세부 설명은 `guides/chapters/`를 봅니다.
- 개발 루프와 보안 기준은 `guides/workflow.md`와 `guides/security.md`와 어긋나지 않게 유지합니다.

## Verification

- 기본 검증은 아래 순서로 실행합니다.

```bash
uv run pytest -q
uv run python -m compileall -q src examples tests
uv lock --check
git diff --check
```

- 실제 provider integration은 필요할 때만 아래처럼 실행합니다.

```bash
RUN_AGENT_LEARNING_INTEGRATION=1 uv run pytest tests/test_openai_integration.py -v
RUN_AGENT_LEARNING_INTEGRATION=1 AGENT_LEARNING_PROVIDER=anthropic uv run pytest tests/test_provider_integration.py -v
```

## Git

- 기존 사용자 변경은 되돌리지 않습니다.
- 작업 중에는 비파괴 명령과 비대화형 git 명령을 우선합니다.
- commit, push, merge가 요청되면 먼저 검증을 끝낸 뒤 진행합니다.
