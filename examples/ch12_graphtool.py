from __future__ import annotations

import sys

from agent_learning.example_support import (
    parse_example_args,
    print_learning_sections,
    print_messages,
    print_model_selection,
    print_tool_schema,
    select_chat_model,
)
from agent_learning.llm.devops_triage import TriageInput, devops_triage_tool
from agent_learning.llm.react_agent import ReActAgentInput, ReActAgentResult, ReActAgentService


def main() -> None:
    args = parse_example_args(sys.argv[1:], "triage checkout 500 errors increased in prod")
    question = args.question
    tools = [devops_triage_tool()]
    selection = select_chat_model("I would triage the service, environment, and symptom before taking action.")
    result = ReActAgentService(selection.model, tools).run(ReActAgentInput(question=question))

    print("graphtool:")
    print_model_selection(selection, verbose=args.verbose)
    print(f"question: {question}")
    print("registered tools: " + ", ".join(tool.name for tool in tools))
    print("input shape: " + ", ".join(TriageInput.model_fields))
    print("steps: " + " -> ".join(step.phase for step in result.steps))
    if args.verbose:
        print_learning_sections(
            goal="LangGraph workflow를 tool로 감싸 ReAct Agent가 subgraph를 action처럼 호출하는 흐름을 봅니다.",
            happens=[
                "ReAct Agent가 devops_triage tool schema를 model에 제공합니다.",
                "tool_node가 devops_triage를 실행하면 내부 LangGraph가 severity, next action, summary node를 순서대로 실행합니다.",
                "graph output은 JSON observation으로 Agent에 돌아가고 final answer 생성에 사용됩니다.",
            ],
            matters="GraphTool은 복잡한 deterministic workflow를 agent의 단일 action으로 숨겨 더 큰 agent 설계를 작게 나눌 수 있게 합니다.",
            try_next=[
                '증상을 바꿔 보세요: uv run python examples/ch12_graphtool.py "triage catalog latency in staging"',
                '상세 trace를 확인하세요: uv run python examples/ch12_graphtool.py --verbose "triage checkout 500 errors increased in prod"',
                '실제 OpenAI 모델로 실행해 보세요: RUN_AGENT_LEARNING_INTEGRATION=1 AGENT_LEARNING_PROVIDER=openai uv run python examples/ch12_graphtool.py "triage checkout 500 errors increased in prod"',
                '실제 Anthropic 모델로 실행해 보세요: RUN_AGENT_LEARNING_INTEGRATION=1 AGENT_LEARNING_PROVIDER=anthropic uv run python examples/ch12_graphtool.py "triage checkout 500 errors increased in prod"',
            ],
        )
        print_tool_schema(tools)
        print("graph nodes:")
        print("- START -> classify_severity")
        print("- classify_severity -> plan_next_actions")
        print("- plan_next_actions -> format_output")
        print("- format_output -> END")
        print_react_steps(result)
        print_messages("messages", result.messages)
    print(f"final answer: {result.answer}")


def print_react_steps(result: ReActAgentResult) -> None:
    print("react steps:")
    for index, step in enumerate(result.steps):
        print(f"- [{index}] {step.phase}: {step.name} -> {step.detail}")
        if step.phase == "observation":
            print(f"observation: {step.detail}")


if __name__ == "__main__":
    main()
