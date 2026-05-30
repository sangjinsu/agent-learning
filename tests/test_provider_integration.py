import pytest

from agent_learning.llm.openai import integration_enabled
from agent_learning.llm.providers import load_provider_config_from_env, new_provider_chat_model
from agent_learning.llm.react_agent import ReActAgentInput, ReActAgentService
from agent_learning.tools.calculator import calculator_tool


pytestmark = pytest.mark.skipif(
    not integration_enabled(),
    reason="set RUN_AGENT_LEARNING_INTEGRATION=1 in the environment or .env to call external APIs",
)


def test_selected_provider_react_agent_integration():
    config = load_provider_config_from_env()
    if not config.active_api_key.strip():
        pytest.skip(f"set {config.active_api_key_name} to run selected provider ReAct integration test")

    model = new_provider_chat_model(config)
    result = ReActAgentService(model, [calculator_tool()]).run(
        ReActAgentInput(
            question='Use the calculator tool to calculate "12 * (7 + 3)", then answer in one short sentence.',
        ),
    )

    assert result.answer.strip()
    assert any(step.phase == "reasoning" for step in result.steps)
    assert any(step.phase == "action" for step in result.steps)
    assert result.tool_messages
