# Notes

## Implementation Notes

- 공식 문서 기준 LangGraph는 `StateGraph`, `START`, `END`, `add_conditional_edges`, `compile`, `invoke` 패턴을 사용합니다.
- 공식 문서 기준 LangChain은 `ChatPromptTemplate`, `ChatOpenAI`, `bind_tools`, `ToolMessage`, `StructuredTool` 패턴을 사용합니다.
- Chapter 09는 embedding/vector store 없이 in-memory keyword retrieval만 다룹니다.
- Chapter 10은 local `stdio` transport로 MCP server process와 client session을 함께 실행합니다.

## Documentation Notes

- README는 빠른 시작과 전체 구조를 보여주는 entrypoint로 유지합니다.
- Chapter별 상세 학습 내용은 `guides/chapters.md`에 둡니다.
- 새 chapter를 추가할 때는 README의 Learning Map, chapter guide, roadmap, progress를 함께 갱신합니다.

## Safety Notes

- 외부 API 호출은 `RUN_AGENT_LEARNING_INTEGRATION=1` 명시 opt-in일 때만 실행합니다.
- 출력에는 API key 값을 포함하지 않습니다.
- 위험한 shell/filesystem/deployment tool은 학습용 tool calling chapter에 등록하지 않습니다.
