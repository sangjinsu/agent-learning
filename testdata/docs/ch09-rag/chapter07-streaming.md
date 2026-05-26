# Chapter 07 Streaming

Streaming returns answer chunks as they are generated instead of waiting for one complete assistant message.
Each AIMessageChunk can be appended to a final answer while a user interface displays progress immediately.
This chapter demonstrates how prompt messages feed model.stream and how collected chunks become the final answer.

한국어 예시:
streaming chunk는 긴 답변을 기다리는 동안 사용자에게 진행 중인 내용을 먼저 보여주는 데 유용합니다.
최종 답변은 여러 chunk를 순서대로 모아서 만들며, UI 체감 속도를 개선합니다.
