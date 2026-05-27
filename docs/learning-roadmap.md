# Learning Roadmap

1. ChatModel 경계를 fake model로 먼저 익힙니다.
2. PromptTemplate으로 system, history, user message 순서를 고정합니다.
3. OpenAI 설정은 `.env`와 환경 변수로 분리합니다.
4. Tool calling은 안전한 calculator만 등록합니다.
5. Chain은 `ChatPromptTemplate | model` 선형 흐름으로 학습합니다.
6. Graph는 calculator branch와 chat branch routing을 보여줍니다.
7. Streaming은 chunk를 수집해 최종 answer로 합칩니다.
8. Observability는 실행 event를 별도 recorder에 남깁니다.
9. RAG는 keyword retriever, context prompt, source metadata에 집중합니다.
10. MCP는 FastMCP server와 stdio client로 tool, resource, prompt 호출 흐름을 보여줍니다.
