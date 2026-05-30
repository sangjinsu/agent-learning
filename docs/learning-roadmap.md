# Learning Roadmap

이 저장소는 agent 애플리케이션을 한 번에 만들기보다, 작은 component를 하나씩 관찰하고 테스트하는 순서로 학습합니다.

## Core Path

1. **ChatModel**: fake model로 질문/응답 service 경계를 먼저 익힙니다.
2. **Prompt Template**: system, history, user message 순서를 고정합니다.
3. **OpenAI ChatModel**: `.env`와 환경 변수로 provider 설정을 분리합니다.
4. **Tool Calling**: 안전한 calculator tool만 등록해 tool call loop를 익힙니다.
5. **Chain**: `ChatPromptTemplate | model` 선형 흐름을 학습합니다.
6. **Graph**: calculator branch와 chat branch routing을 보여줍니다.
7. **Streaming**: chunk를 수집해 최종 answer로 합칩니다.
8. **Observability**: 실행 event를 별도 recorder에 남깁니다.
9. **RAG**: keyword retriever, context prompt, source metadata에 집중합니다.
10. **MCP**: FastMCP server와 stdio client로 tool, resource, prompt 호출 흐름을 보여줍니다.
11. **ReAct Agent**: reasoning, action, observation loop로 model 판단과 tool 실행을 연결합니다.

## Recommended Study Loop

각 chapter는 같은 순서로 봅니다.

1. `README.md`의 Learning Map에서 현재 chapter의 위치를 확인합니다.
2. `guides/chapters.md`에서 chapter별 상세 문서 링크를 열고 목표와 핵심 개념을 읽습니다.
3. `uv run python examples/chXX_*.py ...`로 CLI trace를 확인합니다.
4. `uv run pytest tests/test_chapters.py::<test_name> -q`로 behavior를 검증합니다.
5. 필요할 때만 `RUN_AGENT_LEARNING_INTEGRATION=1`로 실제 OpenAI integration을 실행합니다.

## Expansion Candidates

후속 chapter 후보:

- Memory: conversation state와 long-term store 분리
- Vector RAG: embedding provider와 vector store 도입
- Remote MCP: local stdio 예제를 streamable HTTP connector로 확장
- Evaluation: answer quality와 retrieval quality를 분리해 측정

## Scope Boundaries

- Chapter 09는 embedding/vector store 없이 local keyword retrieval만 다룹니다.
- Chapter 10은 배포용 connector가 아니라 local stdio MCP 학습 예제입니다.
- Chapter 11은 fake model과 calculator tool로 ReAct loop를 관찰하는 local 학습 예제입니다.
- shell, filesystem mutation, deployment tool은 초반 chapter에 등록하지 않습니다.
