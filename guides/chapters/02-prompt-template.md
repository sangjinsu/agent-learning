# Chapter 02. Prompt Template과 Message 설계

## 목표

- LangChain `ChatPromptTemplate`이 변수를 chat message 목록으로 바꾸는 흐름을 이해합니다.
- system prompt, optional chat history, user question 순서의 message 설계를 테스트합니다.
- `ChatService`가 template으로 만든 message를 model에 전달하게 만듭니다.

## 핵심 개념

- `default_chat_prompt()`는 system message, optional `MessagesPlaceholder("history")`, user question을 순서대로 정의합니다.
- `format_messages()`는 blank question을 먼저 거부하고 `list[BaseMessage]`를 반환합니다.
- fake model의 `last_input`으로 실제 model에 들어간 role/content 순서를 검증합니다.

## 실행 명령

```bash
uv run python examples/ch02_prompt_template.py "How does ChatPromptTemplate work?"
```

## 확인할 출력/테스트

CLI에서 확인할 부분:

- `mode: local prompt formatting`으로 API 호출 없이 prompt만 포맷하는지 확인합니다.
- `formatted messages`의 system, history, user message 순서를 확인합니다.
- user question이 마지막 message로 들어가는지 확인합니다.

테스트:

```bash
uv run pytest tests/test_chapters.py::test_ch02_prompt_formats_system_history_and_question -q
```

## 다음 장

Chapter 03에서는 `ChatOpenAI`를 같은 service 경계에 주입합니다.
