# Security Guide

- calculator tool은 Python AST whitelist로 산술식만 평가합니다.
- shell, filesystem mutation, deployment 관련 tool은 등록하지 않습니다.
- `.env`는 commit하지 않고 `.env.example`만 유지합니다.
- 외부 API integration은 `RUN_AGENT_LEARNING_INTEGRATION=1` 명시 opt-in입니다.
