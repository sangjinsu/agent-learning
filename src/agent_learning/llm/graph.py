from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph import END, START, StateGraph

from agent_learning.llm.prompting import format_messages, is_blank_question
from agent_learning.tools.calculator import CalculatorOutput, calculate

ROUTE_CHAT = "chat"
ROUTE_CALCULATOR = "calculator"


@dataclass(frozen=True)
class GraphInput:
    question: str
    history: list[BaseMessage] | None = None


@dataclass(frozen=True)
class GraphResult:
    route: str
    answer: str
    calculation: CalculatorOutput | None = None
    prompt_messages: list[BaseMessage] | None = None
    model_response: BaseMessage | None = None


class _GraphState(TypedDict, total=False):
    question: str
    history: list[BaseMessage]
    route: str
    expression: str
    answer: str
    calculation: CalculatorOutput
    prompt_messages: list[BaseMessage]
    model_response: BaseMessage


class GraphService:
    def __init__(self, model) -> None:
        if model is None:
            raise ValueError("assistant graph: model is required")
        self.model = model
        self.graph = self._compile_graph()

    def run(self, input: GraphInput) -> GraphResult:
        if is_blank_question(input.question):
            raise ValueError("chat service: question must not be blank")
        state = self.graph.invoke({"question": input.question, "history": input.history or []})
        return GraphResult(
            route=state["route"],
            answer=state["answer"],
            calculation=state.get("calculation"),
            prompt_messages=state.get("prompt_messages"),
            model_response=state.get("model_response"),
        )

    def _compile_graph(self):
        builder = StateGraph(_GraphState)
        builder.add_node("route", self._route)
        builder.add_node("calculator", self._calculator)
        builder.add_node("prompt", self._prompt)
        builder.add_node("model", self._model)
        builder.add_edge(START, "route")
        builder.add_conditional_edges(
            "route",
            lambda state: state["route"],
            {ROUTE_CALCULATOR: "calculator", ROUTE_CHAT: "prompt"},
        )
        builder.add_edge("calculator", END)
        builder.add_edge("prompt", "model")
        builder.add_edge("model", END)
        return builder.compile()

    @staticmethod
    def _route(state: _GraphState) -> _GraphState:
        question = state["question"].strip()
        expression = extract_calculation_expression(question)
        if expression:
            return {"question": question, "history": state.get("history", []), "route": ROUTE_CALCULATOR, "expression": expression}
        return {"question": question, "history": state.get("history", []), "route": ROUTE_CHAT}

    @staticmethod
    def _calculator(state: _GraphState) -> _GraphState:
        calculation = calculate(state["expression"])
        return {
            **state,
            "calculation": calculation,
            "answer": f"{calculation.expression} = {_format_number(calculation.result)}",
        }

    @staticmethod
    def _prompt(state: _GraphState) -> _GraphState:
        return {**state, "prompt_messages": format_messages(state["question"], state.get("history", []))}

    def _model(self, state: _GraphState) -> _GraphState:
        response = self.model.invoke(state["prompt_messages"])
        return {**state, "model_response": response, "answer": str(response.content)}


def extract_calculation_expression(question: str) -> str:
    trimmed = question.strip()
    lower = trimmed.lower()
    for prefix in ("calculate:", "calc:", "calculate ", "calc "):
        if lower.startswith(prefix):
            return trimmed[len(prefix) :].strip()
    if re.fullmatch(r"[\d\s+\-*/().]+", trimmed):
        try:
            calculate(trimmed)
        except ValueError:
            return ""
        return trimmed
    return ""


def _format_number(value: float) -> str:
    return str(int(value)) if value.is_integer() else str(value)
