from __future__ import annotations

import sys

from agent_learning.example_support import (
    print_learning_sections,
    print_messages,
    print_model_selection,
    print_tool_schema,
    select_chat_model,
)
from agent_learning.llm.react_agent import ReActAgentInput, ReActAgentResult, ReActAgentService
from agent_learning.tools.calculator import calculator_tool


def main() -> None:
    question = " ".join(sys.argv[1:]) or "12 * (7 + 3)"
    tools = [calculator_tool()]
    selection = select_chat_model("ReAct fallback response.")
    result = ReActAgentService(selection.model, tools).run(
        ReActAgentInput(question=question),
    )

    print_model_selection(selection)
    print_learning_sections(
        goal="ReAct agent가 reasoning, action, observation을 반복한 뒤 final answer로 종료하는 흐름을 봅니다.",
        happens=[
            "llm_call node가 model에게 질문과 tool schema를 주고 tool call 필요 여부를 결정합니다.",
            "tool call이 있으면 tool_node가 allowlist에 있는 calculator만 실행하고 observation을 ToolMessage로 추가합니다.",
            "tool observation이 다시 llm_call로 들어가 final answer가 만들어지면 graph가 종료됩니다.",
        ],
        matters="ReAct는 model 판단과 deterministic tool 실행을 반복 loop로 연결해 더 복잡한 agent workflow의 기본 뼈대가 됩니다.",
        try_next=[
            '계산식을 바꿔 보세요: uv run python examples/ch11_react_agent.py "18 / (2 + 1)"',
            'tool 없이 답하는 경로를 보려면 일반 질문을 넣어 보세요: uv run python examples/ch11_react_agent.py "What is ReAct?"',
            '실제 OpenAI 모델로 실행해 보세요: RUN_AGENT_LEARNING_INTEGRATION=1 AGENT_LEARNING_PROVIDER=openai uv run python examples/ch11_react_agent.py "12 * (7 + 3)"',
            '실제 Anthropic 모델로 실행해 보세요: RUN_AGENT_LEARNING_INTEGRATION=1 AGENT_LEARNING_PROVIDER=anthropic uv run python examples/ch11_react_agent.py "12 * (7 + 3)"',
        ],
    )
    print(f"question: {question}")
    print_tool_schema(tools)
    print("graph nodes:")
    print("- START -> llm_call")
    print("- llm_call -> tool_node when the model requests an action")
    print("- tool_node -> llm_call after observation")
    print("- llm_call -> END when the model returns a final answer")
    print_react_steps(result)
    print_messages("messages", result.messages)
    print(f"final answer: {result.answer}")


def print_react_steps(result: ReActAgentResult) -> None:
    print("react steps:")
    for index, step in enumerate(result.steps):
        print(f"- [{index}] {step.phase}: {step.name} -> {step.detail}")
        if step.phase == "reasoning":
            print(f"reasoning: {step.detail}")
        if step.phase == "action":
            print(f"action: {step.name} {step.detail}")
        if step.phase == "observation":
            print(f"observation: {step.detail}")


if __name__ == "__main__":
    main()
