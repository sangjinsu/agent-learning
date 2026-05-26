# Chapter 04 Tool Calling

Tool calling lets a chat model request a structured tool instead of trying to solve every task in natural language.
The calculator tool exposes a name, description, and args schema so the model can call safe arithmetic deterministically.
After the tool runs, the application returns a ToolMessage and asks the model for a final answer grounded in the tool result.

한국어 예시:
tool calling은 모델이 계산, 검색, DB 조회처럼 정해진 작업을 직접 추측하지 않고 안전한 도구에 맡기게 합니다.
calculator schema와 allowlist는 어떤 tool call을 실행해도 되는지 명확히 제한합니다.
