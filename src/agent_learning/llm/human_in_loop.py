from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt


@dataclass(frozen=True)
class IncidentApprovalInput:
    symptom: str
    service: str
    environment: str
    recommended_action: str


@dataclass(frozen=True)
class IncidentApprovalDecision:
    approved: bool
    reason: str


@dataclass(frozen=True)
class IncidentApprovalResult:
    status: Literal["approved", "rejected"]
    interrupt_payload: dict[str, str]
    trace: list[str]
    final_answer: str
    decision_reason: str


class _ApprovalState(TypedDict, total=False):
    symptom: str
    service: str
    environment: str
    recommended_action: str
    approved: bool
    decision_reason: str
    status: Literal["approved", "rejected"]
    final_answer: str


def run_incident_approval_demo(
    input: IncidentApprovalInput,
    decision: IncidentApprovalDecision,
) -> IncidentApprovalResult:
    _validate_input(input)
    payload = _interrupt_payload(input)
    trace = ["graph -> approval_gate", "interrupt -> approval requested"]
    graph = build_incident_approval_graph()
    config = {"configurable": {"thread_id": _thread_id(input)}}

    graph.invoke(
        {
            "symptom": input.symptom.strip(),
            "service": input.service.strip(),
            "environment": input.environment.strip(),
            "recommended_action": input.recommended_action.strip(),
        },
        config=config,
    )

    trace.append(f"resume -> {_status(decision.approved)}")
    final_state = graph.invoke(
        Command(
            resume={
                "approved": decision.approved,
                "reason": decision.reason.strip(),
            },
        ),
        config=config,
    )
    trace.extend(["graph -> record_decision", "side_effects -> none"])

    return IncidentApprovalResult(
        status=final_state["status"],
        interrupt_payload=payload,
        trace=trace,
        final_answer=final_state["final_answer"],
        decision_reason=final_state["decision_reason"],
    )


def build_incident_approval_graph():
    builder = StateGraph(_ApprovalState)
    builder.add_node("approval_gate", _approval_gate)
    builder.add_node("record_decision", _record_decision)
    builder.add_edge(START, "approval_gate")
    builder.add_edge("record_decision", END)
    return builder.compile(checkpointer=InMemorySaver())


def _approval_gate(state: _ApprovalState) -> Command[Literal["record_decision"]]:
    decision = interrupt(_interrupt_payload_from_state(state))
    return Command(
        update={
            "approved": bool(decision.get("approved")),
            "decision_reason": str(decision.get("reason") or ""),
        },
        goto="record_decision",
    )


def _record_decision(state: _ApprovalState) -> _ApprovalState:
    status = _status(bool(state["approved"]))
    reason = state.get("decision_reason", "").strip()
    final_answer = (
        f"{status}: {state['recommended_action']} for {state['service']} "
        f"in {state['environment']}."
    )
    if status == "rejected" and reason:
        final_answer = f"{final_answer} reason: {reason}"
    return {"status": status, "final_answer": final_answer, "decision_reason": reason}


def _validate_input(input: IncidentApprovalInput) -> None:
    if not input.symptom.strip():
        raise ValueError("human-in-the-loop: symptom must not be blank")
    if not input.service.strip():
        raise ValueError("human-in-the-loop: service must not be blank")
    if not input.environment.strip():
        raise ValueError("human-in-the-loop: environment must not be blank")
    if not input.recommended_action.strip():
        raise ValueError("human-in-the-loop: recommended action must not be blank")


def _interrupt_payload(input: IncidentApprovalInput) -> dict[str, str]:
    return {
        "question": "Approve this incident action?",
        "service": input.service.strip(),
        "environment": input.environment.strip(),
        "symptom": input.symptom.strip(),
        "recommended_action": input.recommended_action.strip(),
    }


def _interrupt_payload_from_state(state: _ApprovalState) -> dict[str, str]:
    return _interrupt_payload(
        IncidentApprovalInput(
            symptom=state["symptom"],
            service=state["service"],
            environment=state["environment"],
            recommended_action=state["recommended_action"],
        ),
    )


def _status(approved: bool) -> Literal["approved", "rejected"]:
    return "approved" if approved else "rejected"


def _thread_id(input: IncidentApprovalInput) -> str:
    return "incident-gate-" + "-".join(
        part.strip().lower().replace(" ", "-")
        for part in (input.environment, input.service)
        if part.strip()
    )
