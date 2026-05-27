# Chapter Guide

각 chapter는 `examples/chXX_*.py`에서 실행 흐름을 확인하고, `tests/test_chapters.py`에서 외부 API 없는 behavior를 검증합니다.
실제 OpenAI 연동은 `tests/test_openai_integration.py`에 모아 두고 `RUN_AGENT_LEARNING_INTEGRATION=1`일 때만 실행합니다.

Go판의 Eino component 개념은 Python에서 다음처럼 대응합니다.

- `ChatModel` -> LangChain chat model `invoke`/`stream`
- `ChatTemplate` -> `ChatPromptTemplate`
- `WithTools` -> `bind_tools`
- `ToolsNode` -> local `ToolMessage` execution loop
- `Graph` -> LangGraph `StateGraph`
- `Retriever` -> `InMemoryKeywordRetriever`
- `MCP server` -> `FastMCP` + `ClientSession` stdio demo

Chapter별 integration coverage:

- Chapter 03: `ChatOpenAI` factory와 `ChatService`
- Chapter 04: `bind_tools` 기반 calculator tool calling
- Chapter 05: runnable chain과 history prompt
- Chapter 06: LangGraph calculator/chat routing
- Chapter 07: streaming chunk collection
- Chapter 08: observable chain event recording
- Chapter 09: keyword RAG, context prompt, source metadata
- Chapter 10: local MCP stdio server/client, tool/resource/prompt
