from __future__ import annotations

import json
import operator
from dataclasses import asdict, dataclass
from typing import Annotated, Any, Literal, TypedDict

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import BaseTool
from langgraph.graph import END, START, StateGraph

from agent_learning.llm.prompting import is_blank_question


REACT_SYSTEM_PROMPT = (
    "You are a ReAct learning agent. Decide whether the user needs a tool. "
    "If a calculator tool is useful, call it. After observing tool results, "
    "return the final answer."
)


@dataclass(frozen=True)
class ReActAgentInput:
    question: str
    history: list[BaseMessage] | None = None


@dataclass(frozen=True)
class ReActStep:
    phase: Literal["reasoning", "action", "observation", "final"]
    name: str
    detail: str


@dataclass(frozen=True)
class ReActAgentResult:
    messages: list[BaseMessage]
    tool_messages: list[ToolMessage]
    steps: list[ReActStep]
    answer: str


class _ReActState(TypedDict):
    messages: Annotated[list[BaseMessage], operator.add]
    steps: Annotated[list[ReActStep], operator.add]


class ReActAgentService:
    def __init__(self, model, tools: list[BaseTool]) -> None:
        if model is None:
            raise ValueError("react agent: model is required")
        if not hasattr(model, "bind_tools"):
            raise ValueError("react agent: model must support tool calling")
        self.tool_by_name = {tool.name: tool for tool in tools}
        self.model = model.bind_tools(tools)
        self.graph = self._compile_graph()

    def run(self, input: ReActAgentInput) -> ReActAgentResult:
        if is_blank_question(input.question):
            raise ValueError("react agent: question must not be blank")
        initial_messages = [*(input.history or []), HumanMessage(content=input.question)]
        state = self.graph.invoke({"messages": initial_messages, "steps": []})
        messages = state["messages"]
        return ReActAgentResult(
            messages=messages,
            tool_messages=[message for message in messages if isinstance(message, ToolMessage)],
            steps=state["steps"],
            answer=_final_answer(messages),
        )

    def _compile_graph(self):
        builder = StateGraph(_ReActState)
        builder.add_node("llm_call", self._llm_call)
        builder.add_node("tool_node", self._tool_node)
        builder.add_edge(START, "llm_call")
        builder.add_conditional_edges(
            "llm_call",
            _should_continue,
            {"tool_node": "tool_node", END: END},
        )
        builder.add_edge("tool_node", "llm_call")
        return builder.compile()

    def _llm_call(self, state: _ReActState) -> _ReActState:
        response = self.model.invoke([SystemMessage(content=REACT_SYSTEM_PROMPT), *state["messages"]])
        tool_calls = getattr(response, "tool_calls", []) or []
        if tool_calls:
            detail = ", ".join(call["name"] for call in tool_calls)
            step = ReActStep("reasoning", "model", f"model requested tool call(s): {detail}")
        else:
            step = ReActStep("final", "model", str(response.content))
        return {"messages": [response], "steps": [step]}

    def _tool_node(self, state: _ReActState) -> _ReActState:
        last_message = state["messages"][-1]
        messages: list[ToolMessage] = []
        steps: list[ReActStep] = []
        for call in getattr(last_message, "tool_calls", []) or []:
            name = call["name"]
            if name not in self.tool_by_name:
                raise ValueError(f"react agent: tool is not allowed: {name}")
            args = call.get("args", {})
            result = self.tool_by_name[name].invoke(args)
            content = _json_content(result)
            messages.append(
                ToolMessage(
                    content=content,
                    tool_call_id=call.get("id") or name,
                    name=name,
                )
            )
            steps.append(ReActStep("action", name, _json_content(args)))
            steps.append(ReActStep("observation", name, content))
        return {"messages": messages, "steps": steps}


def _should_continue(state: _ReActState) -> Literal["tool_node", "__end__"]:
    last_message = state["messages"][-1]
    if getattr(last_message, "tool_calls", []) or []:
        return "tool_node"
    return END


def _final_answer(messages: list[BaseMessage]) -> str:
    for message in reversed(messages):
        if isinstance(message, AIMessage):
            return str(message.content)
    return ""


def _json_content(value: Any) -> str:
    if hasattr(value, "__dataclass_fields__"):
        value = asdict(value)
    return json.dumps(value, ensure_ascii=False, sort_keys=True)
