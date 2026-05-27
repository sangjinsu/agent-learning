from __future__ import annotations

import asyncio
import sys

from agent_learning.example_support import print_learning_sections
from agent_learning.mcp_demo import MCPDemoResult, normalize_flow, run_mcp_demo


DEFAULT_CHAPTER_BY_FLOW = {
    "discover": "mcp",
    "resource": "resource",
    "prompt": "prompt",
    "tool": "tool",
    "full": "mcp",
}


def main() -> None:
    flow, chapter = parse_cli(sys.argv[1:])
    result = asyncio.run(run_mcp_demo(chapter, flow=flow))

    print("mode: local mcp stdio")
    print(f"mcp flow: {result.flow}")
    print(f"target chapter: {chapter}")
    print_learning_sections(
        goal="MCP server가 tool, resource, prompt를 노출하고 client가 표준 protocol로 호출하는 흐름을 봅니다.",
        happens=[
            "FastMCP server가 summarize_chapter tool, chapter resource template, review_chapter prompt를 등록합니다.",
            "stdio client가 server process를 시작하고 ClientSession.initialize()로 protocol handshake를 수행합니다.",
            "discover/resource/prompt/tool/full 모드로 capability discovery와 primitive 호출을 나누어 관찰합니다.",
        ],
        matters="MCP를 사용하면 agent host가 특정 앱 코드에 직접 묶이지 않고 표준 protocol로 외부 capability를 발견하고 사용할 수 있습니다.",
        try_next=[
            'capability discovery만 보려면 실행하세요: uv run python examples/ch10_mcp.py discover',
            'primitive별 호출을 비교하세요: uv run python examples/ch10_mcp.py resource | prompt | tool',
            '전체 흐름을 보려면 실행하세요: uv run python examples/ch10_mcp.py full',
        ],
    )
    print_result(result)


def parse_cli(args: list[str]) -> tuple[str, str]:
    if not args:
        return "full", DEFAULT_CHAPTER_BY_FLOW["full"]

    first = args[0].strip().lower()
    try:
        flow = normalize_flow(first)
    except ValueError:
        chapter = " ".join(args)
        return "full", chapter

    if first == "mcp":
        return flow, "mcp"

    chapter = " ".join(args[1:]) or DEFAULT_CHAPTER_BY_FLOW[flow]
    return flow, chapter


def print_result(result: MCPDemoResult) -> None:
    print("server transport: stdio")
    print("mcp call trace:")
    for step in result.trace:
        print(f"- {step}")
    print("available tools:")
    for name in result.tool_names:
        print(f"- {name}")
    print("available resources:")
    for template in result.resource_templates:
        print(f"- {template}")
    print("available prompts:")
    for name in result.prompt_names:
        print(f"- {name}")
    if result.resource_content:
        print(f"resource content: {result.resource_content}")
    if result.prompt_text:
        print(f"prompt messages: {result.prompt_text}")
    if result.tool_result:
        print(f"tool result: {result.tool_result}")
    print(f"final answer: {result.final_answer}")


if __name__ == "__main__":
    main()
