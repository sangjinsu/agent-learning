from __future__ import annotations

import sys

from agent_learning.example_support import parse_example_args, print_key_values, print_learning_sections
from agent_learning.llm.human_in_loop import (
    IncidentApprovalDecision,
    IncidentApprovalInput,
    IncidentApprovalResult,
    run_incident_approval_demo,
)


def main() -> None:
    args = parse_example_args(sys.argv[1:], "triage checkout 500 errors increased in prod")
    incident_input = _incident_input_from_question(args.question)
    decision = IncidentApprovalDecision(approved=True, reason="customer impact is confirmed")
    result = run_incident_approval_demo(incident_input, decision)

    print("human-in-the-loop:")
    print("mode: local")
    print(f"question: {args.question}")
    print(f"decision: {'approve' if decision.approved else 'reject'}")
    print(f"status: {result.status}")
    if args.verbose:
        print_learning_sections(
            goal="LangGraph interrupt로 action 실행 전 사람의 승인/거절 gate를 관찰합니다.",
            happens=[
                "approval_gate node가 incident action details를 interrupt payload로 노출합니다.",
                "caller는 같은 thread_id에서 Command(resume=...)로 승인 또는 거절 결정을 전달합니다.",
                "record_decision node는 결정만 기록하고 paging, rollback, deployment 같은 side effect는 실행하지 않습니다.",
            ],
            matters="Human-in-the-loop은 agent가 위험한 action을 자동 실행하지 않고 사람의 판단을 workflow boundary에 넣는 안전 장치입니다.",
            try_next=[
                '거절 흐름을 코드에서 바꿔 보세요: IncidentApprovalDecision(approved=False, reason="watch first")',
                '상세 trace를 확인하세요: uv run python examples/ch13_human_in_loop.py --verbose "triage catalog latency in staging"',
                "Chapter 12 GraphTool의 next_actions 중 하나를 recommended_action으로 넘기는 흐름을 비교해 보세요.",
            ],
        )
        print("graph nodes:")
        print("- START -> approval_gate")
        print("- approval_gate -> interrupt")
        print("- Command(resume=...) -> record_decision")
        print("- record_decision -> END")
        print_key_values("interrupt payload", result.interrupt_payload)
        print_key_values(
            "resume command",
            {
                "approved": decision.approved,
                "reason": decision.reason,
            },
        )
        print_approval_trace(result)
    print(f"final answer: {result.final_answer}")


def print_approval_trace(result: IncidentApprovalResult) -> None:
    print("approval trace:")
    for index, item in enumerate(result.trace):
        print(f"- [{index}] {item}")


def _incident_input_from_question(question: str) -> IncidentApprovalInput:
    text = question.strip()
    lower = text.lower()
    environment = "prod" if "prod" in lower or "production" in lower else "staging"
    service = "checkout"
    for candidate in ("checkout", "catalog", "payment", "payments", "search", "auth"):
        if candidate in lower:
            service = "payment" if candidate == "payments" else candidate
            break

    symptom = text
    if lower.startswith("triage "):
        symptom = text[len("triage ") :].strip()
    recommended_action = _recommended_action(symptom, service, environment)
    return IncidentApprovalInput(
        symptom=symptom,
        service=service,
        environment=environment,
        recommended_action=recommended_action,
    )


def _recommended_action(symptom: str, service: str, environment: str) -> str:
    lower = symptom.lower()
    if environment == "prod" and ("500" in lower or "error" in lower or "down" in lower):
        return f"page the {service} on-call"
    if "latency" in lower or "slow" in lower or "timeout" in lower:
        return f"open an incident note for {service}"
    return f"watch {environment} {service} dashboards"


if __name__ == "__main__":
    main()
