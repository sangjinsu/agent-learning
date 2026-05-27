from __future__ import annotations

import argparse
import asyncio
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.server.fastmcp import FastMCP


CHAPTER_NOTES = {
    "mcp": (
        "Chapter 10 MCP explains Model Context Protocol as a standard way for hosts "
        "to discover and call server-provided tools, resources, and prompts."
    ),
    "tool": (
        "MCP tools are callable actions with structured input. They are useful when "
        "a host needs deterministic capabilities outside the model itself."
    ),
    "resource": (
        "MCP resources expose read-only context such as documents, records, or local "
        "notes that a host can browse and attach to a conversation."
    ),
    "prompt": (
        "MCP prompts package reusable instructions so a host can offer consistent "
        "workflows without copying prompt text into every client."
    ),
}


@dataclass(frozen=True)
class MCPDemoResult:
    flow: str
    trace: list[str]
    tool_names: list[str]
    resource_templates: list[str]
    prompt_names: list[str]
    resource_content: str
    prompt_text: str
    tool_result: str
    final_answer: str


def chapter_note(chapter: str) -> str:
    key = chapter.strip().lower()
    if key not in CHAPTER_NOTES:
        raise ValueError(f"unknown chapter: {chapter}")
    return CHAPTER_NOTES[key]


def create_mcp_server() -> FastMCP:
    server = FastMCP("Agent Learning MCP")

    @server.tool()
    def summarize_chapter(chapter: str = "mcp") -> str:
        """Return a short learning summary for an agent-learning chapter."""
        note = chapter_note(chapter)
        return f"MCP connects hosts to external capabilities. {note}"

    @server.resource("chapter://{chapter}")
    def read_chapter(chapter: str) -> str:
        """Read a short chapter note as MCP resource content."""
        return chapter_note(chapter)

    @server.prompt()
    def review_chapter(chapter: str = "mcp") -> str:
        """Build a short review prompt for a chapter."""
        note = chapter_note(chapter)
        return f"Review Chapter 10 MCP. Explain this note in two concise bullets: {note}"

    return server


def run_server_stdio() -> None:
    create_mcp_server().run(transport="stdio")


async def run_mcp_demo(chapter: str = "mcp", flow: str = "full") -> MCPDemoResult:
    selected_flow = normalize_flow(flow)
    server_params = _server_parameters()
    with open(os.devnull, "w") as errlog:
        async with stdio_client(server_params, errlog=errlog) as (read, write):
            async with ClientSession(read, write) as session:
                trace: list[str] = []

                trace.append("client -> initialize")
                await session.initialize()
                trace.append("server -> initialized session")

                trace.append("client -> list_tools")
                tools = await session.list_tools()
                tool_names = [tool_info.name for tool_info in tools.tools]
                trace.append(f"server -> tools: {_join_names(tool_names)}")

                trace.append("client -> list_resource_templates")
                resource_templates = await session.list_resource_templates()
                resource_template_names = [
                    str(template.uriTemplate)
                    for template in resource_templates.resourceTemplates
                ]
                trace.append(f"server -> resource templates: {_join_names(resource_template_names)}")

                trace.append("client -> list_prompts")
                prompts = await session.list_prompts()
                prompt_names = [prompt_info.name for prompt_info in prompts.prompts]
                trace.append(f"server -> prompts: {_join_names(prompt_names)}")

                resource_content = ""
                prompt_text = ""
                tool_result = ""

                if selected_flow in {"full", "resource"}:
                    resource_uri = f"chapter://{chapter}"
                    trace.append(f"client -> read_resource uri={resource_uri}")
                    resource = await session.read_resource(resource_uri)
                    resource_content = _first_text(resource.contents)
                    trace.append(f"server -> resource text: {resource_content}")

                if selected_flow in {"full", "prompt"}:
                    prompt_arguments = {"chapter": chapter}
                    trace.append(
                        "client -> get_prompt "
                        f"name=review_chapter arguments={prompt_arguments}"
                    )
                    prompt = await session.get_prompt(
                        "review_chapter",
                        arguments=prompt_arguments,
                    )
                    prompt_text = _prompt_text(prompt.messages)
                    trace.append(f"server -> prompt messages: {prompt_text}")

                if selected_flow in {"full", "tool"}:
                    tool_arguments = {"chapter": chapter}
                    trace.append(
                        "client -> call_tool "
                        f"name=summarize_chapter arguments={tool_arguments}"
                    )
                    tool = await session.call_tool(
                        "summarize_chapter",
                        arguments=tool_arguments,
                    )
                    tool_result = _first_text(tool.content)
                    trace.append(f"server -> tool result: {tool_result}")

                return MCPDemoResult(
                    flow=selected_flow,
                    trace=trace,
                    tool_names=tool_names,
                    resource_templates=resource_template_names,
                    prompt_names=prompt_names,
                    resource_content=resource_content,
                    prompt_text=prompt_text,
                    tool_result=tool_result,
                    final_answer=f"MCP stdio {selected_flow} demo completed.",
                )


def normalize_flow(flow: str) -> str:
    selected_flow = flow.strip().lower()
    if selected_flow == "mcp":
        return "full"
    if selected_flow in {"discover", "resource", "prompt", "tool", "full"}:
        return selected_flow
    raise ValueError(f"unknown MCP demo flow: {flow}")


def _server_parameters() -> StdioServerParameters:
    root = Path(__file__).resolve().parents[2]
    env = os.environ.copy()
    src_path = str(root / "src")
    existing_pythonpath = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = (
        src_path
        if not existing_pythonpath
        else f"{src_path}{os.pathsep}{existing_pythonpath}"
    )
    return StdioServerParameters(
        command=sys.executable,
        args=["-m", "agent_learning.mcp_demo", "server"],
        env=env,
    )


def _join_names(names: Iterable[str]) -> str:
    values = list(names)
    if not values:
        return "(none)"
    return ", ".join(values)


def _first_text(contents: Iterable[object]) -> str:
    for content in contents:
        text = getattr(content, "text", None)
        if text is not None:
            return str(text)
    return ""


def _prompt_text(messages: Iterable[object]) -> str:
    parts: list[str] = []
    for message in messages:
        content = getattr(message, "content", None)
        text = getattr(content, "text", None)
        if text is not None:
            parts.append(str(text))
    return "\n".join(parts)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Agent Learning MCP demo server")
    parser.add_argument("command", choices=["server"], help="Run the local MCP server over stdio")
    args = parser.parse_args(argv)
    if args.command == "server":
        run_server_stdio()


if __name__ == "__main__":
    main()
