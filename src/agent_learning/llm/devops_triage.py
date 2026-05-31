from __future__ import annotations

from typing import TypedDict

from langgraph.graph import START, StateGraph
from pydantic import BaseModel, Field

from agent_learning.tools.graph_tool import graph_tool_from_runnable


class TriageInput(BaseModel):
    symptom: str = Field(description="Observed production or staging symptom.")
    service: str = Field(description="Service or component where the symptom appears.")
    environment: str = Field(description="Runtime environment, such as prod or staging.")


class TriageOutput(BaseModel):
    symptom: str
    service: str
    environment: str
    severity: str
    suspected_area: str
    next_actions: list[str]
    summary: str


class _TriageState(TypedDict, total=False):
    symptom: str
    service: str
    environment: str
    severity: str
    suspected_area: str
    next_actions: list[str]
    summary: str


def build_devops_triage_graph():
    builder = StateGraph(_TriageState)
    builder.add_node("classify_severity", _classify_severity)
    builder.add_node("plan_next_actions", _plan_next_actions)
    builder.add_node("format_output", _format_output)
    builder.add_edge(START, "classify_severity")
    builder.add_edge("classify_severity", "plan_next_actions")
    builder.add_edge("plan_next_actions", "format_output")
    builder.set_finish_point("format_output")
    return builder.compile()


def run_devops_triage(input: dict[str, str]) -> dict[str, str | list[str]]:
    state = build_devops_triage_graph().invoke(input)
    return TriageOutput(**state).model_dump()


def devops_triage_tool():
    return graph_tool_from_runnable(
        name="devops_triage",
        description="Classify a DevOps incident symptom and suggest deterministic next actions.",
        args_schema=TriageInput,
        runnable=build_devops_triage_graph(),
    )


def _classify_severity(state: _TriageState) -> _TriageState:
    symptom = state["symptom"].lower()
    environment = state["environment"].lower()
    service = state["service"]
    high_markers = ("500", "error", "errors", "down", "outage", "failed", "increased")
    medium_markers = ("latency", "slow", "timeout", "timeouts", "degraded")

    if environment == "prod" and any(marker in symptom for marker in high_markers):
        severity = "high"
    elif any(marker in symptom for marker in medium_markers):
        severity = "medium"
    else:
        severity = "low"

    if "500" in symptom or "error" in symptom:
        suspected_area = f"{service} application errors"
    elif "latency" in symptom or "slow" in symptom or "timeout" in symptom:
        suspected_area = f"{service} latency path"
    else:
        suspected_area = f"{service} service health"

    return {"severity": severity, "suspected_area": suspected_area}


def _plan_next_actions(state: _TriageState) -> _TriageState:
    service = state["service"]
    environment = state["environment"]
    severity = state["severity"]

    if severity == "high":
        actions = [
            f"page the {service} on-call",
            f"check recent {service} deploys in {environment}",
            f"inspect {environment} {service} error logs",
            "prepare rollback if customer impact continues",
        ]
    elif severity == "medium":
        actions = [
            f"compare {service} latency dashboards against baseline",
            f"inspect {environment} dependency health",
            "open an incident note if symptoms continue for 15 minutes",
        ]
    else:
        actions = [
            f"record the {service} symptom",
            f"watch {environment} dashboards for recurrence",
            "avoid paging until impact is confirmed",
        ]

    return {"next_actions": actions}


def _format_output(state: _TriageState) -> _TriageState:
    summary = (
        f"{state['service']} in {state['environment']} is {state['severity']} severity; "
        f"suspected area is {state['suspected_area']}."
    )
    return {"summary": summary}
