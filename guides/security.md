# Security Guide

## API Keys

- `.env`는 commit하지 않고 `.env.example`만 유지합니다.
- `OPENAI_API_KEY` 값은 출력하지 않습니다.
- 외부 API integration은 `RUN_AGENT_LEARNING_INTEGRATION=1` 명시 opt-in입니다.

## Tool Calling

- calculator tool은 Python AST whitelist로 산술식만 평가합니다.
- bool literal, function call, attribute access, import 같은 expression은 거부합니다.
- shell, filesystem mutation, deployment 관련 tool은 등록하지 않습니다.

## Local Data

- Chapter 09 RAG는 `testdata/docs/ch09-rag`의 local text data만 읽습니다.
- Chapter 10 MCP는 local stdio demo이며 remote connector auth나 production deployment를 다루지 않습니다.
